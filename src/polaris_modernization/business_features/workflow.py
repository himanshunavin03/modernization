"""Prepare, validate, and persist PO/BA-quality Business Feature specifications."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from polaris_modernization.business_features.models import ApiRelationshipPath, BusinessFeatureCatalog, BusinessFeatureReasoningSubmission, TraceableStatement
from polaris_modernization.business_features.retrieval import build_business_feature_packages, load_approved_features


class UnsupportedBusinessClaimsError(ValueError):
    """Business interpretation is stale or unsupported by approved Feature evidence."""


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _run_path(root: Path, project_id: str) -> tuple[str, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S-%f")
    run_id = f"{project_id}-{timestamp}"
    return run_id, root / run_id


def _manifest(packages: list) -> tuple[dict[str, str], str]:
    values = {item.package_id: item.package_hash for item in packages}
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return values, sha256(encoded).hexdigest()


def prepare_business_feature_enrichment(feature_root: Path, output_root: Path) -> dict:
    approved = load_approved_features(feature_root)
    packages = build_business_feature_packages(approved)
    project_id = approved["catalog"]["project_id"]
    run_id, destination = _run_path(output_root / "prepared", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    package_map, manifest_hash = _manifest(packages)
    _write_json(destination / "business-feature-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write_json(destination / "business-feature-evidence-manifest.json", {
        "kg_run_id": approved["catalog"]["kg_run_id"], "application_understanding_run_id": approved["catalog"]["application_understanding_run_id"],
        "feature_run_id": approved["run_id"], "manifest_hash": manifest_hash, "packages": package_map,
    })
    _write_json(destination / "business-feature-reasoning-schema.json", BusinessFeatureReasoningSubmission.model_json_schema())
    (destination / "agent-instructions.md").write_text(
        "# PO/BA Enrichment Instructions\n\nRead only these packages. Preserve Feature IDs, names, workflows, API statuses, and evidence. "
        "Label inferred value, concerns, assumptions, limitations, risks, and success indicators. Do not invent actors, rules, KPIs, or requirements. "
        "Open questions must remain questions. Produce no User Stories or Acceptance Criteria.\n", encoding="utf-8",
    )
    _write_json(destination / "preparation.json", {
        "project_id": project_id, "kg_run_id": approved["catalog"]["kg_run_id"],
        "application_understanding_run_id": approved["catalog"]["application_understanding_run_id"],
        "feature_run_id": approved["run_id"], "business_feature_evidence_packages": len(packages),
        "evidence_package_manifest_hash": manifest_hash, "external_llm_api_calls": 0,
    })
    return {"run_id": run_id, "path": destination, "approved": approved, "packages": packages}


def _all_statements(specification) -> list[TraceableStatement]:
    return [
        specification.current_objective, specification.modernization_objective,
        *specification.business_value, *specification.current_business_functionality,
        *specification.information_involved, *specification.current_user_experience,
        *specification.evidence_backed_limitations, *specification.modernization_concerns,
        *specification.in_scope, *specification.out_of_scope, *specification.assumptions,
        *specification.risks_and_limitations, *specification.success_indicators,
    ]


def _api_paths(source: dict, approved: dict) -> list[dict]:
    packages = [item for item in approved["packages"] if item["package_id"] in source["evidence_package_ids"]]
    workflows = {
        workflow["name"]: workflow
        for package in packages for workflow in package.get("objects", {}).get("workflows", [])
    }
    paths = []
    for contract in source["api_contracts"]:
        workflow = workflows.get(contract["workflow"], {})
        evidence = workflow.get("evidence", [])
        call = next((item for item in evidence if ":ApiCall:" in item.get("node_id", "")), None)
        endpoint = next((item for item in evidence if ":Endpoint:" in item.get("node_id", "")), None)
        paths.append({
            "workflow": contract["workflow"], "status": contract["status"],
            "frontend_source": call.get("source_path", "UNRESOLVED") if call else "UNRESOLVED",
            "api_contract": call["node_id"].split(":ApiCall:", 1)[1] if call else "UNRESOLVED",
            "backend_endpoint": endpoint["node_id"].split(":Endpoint:", 1)[1] if endpoint else contract["status"],
        })
    return paths


def _validate_submission(submission: BusinessFeatureReasoningSubmission, approved: dict, packages: list) -> dict:
    catalog = approved["catalog"]
    capability_coverage = catalog.get("capability_coverage", {})
    if capability_coverage.get("status") == "FAIL" or capability_coverage.get("silently_dropped_capabilities"):
        raise UnsupportedBusinessClaimsError("Upstream source capability coverage is incomplete.")
    _, manifest_hash = _manifest(packages)
    expected_lineage = (catalog["kg_run_id"], catalog["application_understanding_run_id"], approved["run_id"])
    if (submission.kg_run_id, submission.application_understanding_run_id, submission.feature_run_id) != expected_lineage:
        raise UnsupportedBusinessClaimsError("Business Feature submission references stale upstream lineage.")
    if submission.evidence_package_manifest_hash != manifest_hash:
        raise UnsupportedBusinessClaimsError("Business Feature evidence manifest hash is stale.")
    upstream = {item["feature_id"]: item for item in catalog["features"]}
    submitted = {item.feature_id: item for item in submission.business_features}
    if len(submitted) != len(submission.business_features) or set(submitted) != set(upstream):
        raise UnsupportedBusinessClaimsError("Feature IDs or Feature count changed during enrichment.")
    package_map = {item.package_id: item for item in packages}
    for feature_id, spec in submitted.items():
        source = upstream[feature_id]
        expected_package_id = f"business-feature:{feature_id}"
        if spec.feature_name != source["title"] or spec.functional_module != source["module"] or spec.evidence_package_id != expected_package_id:
            raise UnsupportedBusinessClaimsError("Feature identity changed during enrichment.")
        if set(spec.business_capabilities) != set(source["business_capabilities"]) or {item.name for item in spec.capability_details} != set(source["business_capabilities"]):
            raise UnsupportedBusinessClaimsError("Business capability references changed during enrichment.")
        if {item.name for item in spec.workflows} != set(source["workflows"]):
            raise UnsupportedBusinessClaimsError("Every approved Feature workflow must have exactly one Business workflow specification.")
        if {item.name for item in spec.domain_concepts} != set(source["domain_concepts"]):
            raise UnsupportedBusinessClaimsError("Domain concept references changed during enrichment.")
        if {item.source_rule for item in spec.business_rules} != set(source["business_rules"]):
            raise UnsupportedBusinessClaimsError("Business rules were invented or omitted.")
        if source["business_rules"] and spec.no_business_rules_marker or not source["business_rules"] and spec.no_business_rules_marker != "NO_EVIDENCE_BACKED_BUSINESS_RULES_IDENTIFIED":
            raise UnsupportedBusinessClaimsError("No-business-rules state is not represented honestly.")
        if {item.name for item in spec.dependencies} != set(source["dependencies"]):
            raise UnsupportedBusinessClaimsError("Dependency references changed during enrichment.")
        if spec.actors:
            raise UnsupportedBusinessClaimsError("Approved Features contain no evidence-supported actors/personas.")
        expected_api = {(item["workflow"], item["status"]) for item in source["api_contracts"]}
        actual_api = {(item.workflow, item.status) for item in spec.api_integration.relationships}
        if actual_api != expected_api:
            raise UnsupportedBusinessClaimsError("API status was upgraded, omitted, or invented.")
        counts = {status: sum(1 for _, value in expected_api if value == status) for status in ("PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE")}
        if (spec.api_integration.proven, spec.api_integration.unresolved, spec.api_integration.dynamic, spec.api_integration.external, spec.api_integration.no_backend_route) != tuple(counts[key] for key in ("PROVEN", "UNRESOLVED", "DYNAMIC", "EXTERNAL", "NO_BACKEND_ROUTE")):
            raise UnsupportedBusinessClaimsError("API profile counts do not match approved relationships.")
        expected_paths = _api_paths(source, approved)
        if spec.api_integration.paths and [item.model_dump(mode="json") for item in spec.api_integration.paths] != expected_paths:
            raise UnsupportedBusinessClaimsError("API path details do not match approved evidence packages.")
        spec.api_integration.paths = [ApiRelationshipPath.model_validate(item) for item in expected_paths]
        if any(path["status"] == "PROVEN" and "UNRESOLVED" in {path["frontend_source"], path["api_contract"], path["backend_endpoint"]} for path in expected_paths):
            raise UnsupportedBusinessClaimsError("A PROVEN API relationship lacks its approved frontend, contract, or endpoint path.")
        api_by_workflow = dict(expected_api)
        for workflow in spec.workflows:
            expected_status = api_by_workflow.get(workflow.name, "NOT_APPLICABLE")
            if workflow.api_status != expected_status or any(ui not in source["ui_surfaces"] for ui in workflow.supporting_ui):
                raise UnsupportedBusinessClaimsError("Business workflow changed its API status or supporting UI evidence.")
        allowed_evidence = {(item["node_id"], item["source_path"], item["line_start"], item["line_end"], item["provenance"]) for item in source["source_evidence"]}
        allowed_nodes = set(source["kg_evidence"])
        references = [*spec.source_evidence]
        references += [ref for statement in _all_statements(spec) for ref in statement.evidence]
        references += [ref for item in [*spec.actors, *spec.capability_details, *spec.workflows, *spec.business_rules, *spec.domain_concepts, *spec.dependencies, *spec.open_questions] for ref in item.evidence]
        if any((ref.node_id, ref.source_path, ref.line_start, ref.line_end, ref.provenance) not in allowed_evidence for ref in references):
            raise UnsupportedBusinessClaimsError("Business statement references unsupported source evidence.")
        if any(node not in allowed_nodes for node in spec.kg_evidence):
            raise UnsupportedBusinessClaimsError("Business Feature references unsupported KG evidence.")
        if any(item.classification != "INFERRED_BUSINESS_VALUE" for item in spec.business_value):
            raise UnsupportedBusinessClaimsError("Business value without requirement evidence must remain explicitly inferred.")
        if any(item.classification != "ASSUMPTION" for item in spec.assumptions):
            raise UnsupportedBusinessClaimsError("Assumptions must be explicitly labeled.")
        if any(item.classification != "MODERNIZATION_CONCERN" for item in spec.modernization_concerns):
            raise UnsupportedBusinessClaimsError("Modernization concerns must be explicitly labeled.")
        if any(item.classification != "MODERNIZATION_SUCCESS_INDICATOR" for item in spec.success_indicators):
            raise UnsupportedBusinessClaimsError("Success indicators must be modernization indicators, not historical KPIs.")
        if any(not item.question.rstrip().endswith("?") for item in spec.open_questions):
            raise UnsupportedBusinessClaimsError("Open questions must remain questions, not requirements.")
        if any(re.search(r"\b\d+\s*%|increase by|reduce by", item.text, re.I) for item in spec.success_indicators):
            raise UnsupportedBusinessClaimsError("Fabricated numeric business KPIs are not allowed.")
    all_specs = list(submitted.values())
    return {
        "feature_ids_preserved": True, "feature_count_preserved": True,
        "provenance_validation": "PASS", "business_feature_validation": "PASS", "business_quality_validation": "PASS",
        "unsupported_business_claims_rejected": 0,
        "actors_identified": sum(len(item.actors) for item in all_specs),
        "domain_concepts_used": len({value.name for item in all_specs for value in item.domain_concepts}),
        "business_rules_used": len({value.source_rule for item in all_specs for value in item.business_rules}),
        "dependencies_used": len({value.name for item in all_specs for value in item.dependencies}),
        "assumptions": sum(len(item.assumptions) for item in all_specs),
        "open_questions": sum(len(item.open_questions) for item in all_specs),
        "inferred_business_value_claims": sum(len(item.business_value) for item in all_specs),
        "capability_completeness": capability_coverage.get("status", "NOT_AVAILABLE"),
    }


def _feature_markdown(spec) -> str:
    def bullets(values) -> str:
        return "\n".join(f"- {value}" for value in values) if values else "- None identified from approved evidence."
    lines = [f"# {spec.feature_name}", "", f"**Feature ID:** `{spec.feature_id}`  ", f"**Module:** {spec.functional_module}  ", f"**Capabilities:** {', '.join(spec.business_capabilities)}  ", f"**Confidence:** `{spec.confidence.level}`", "", "## Executive Description", "", *spec.executive_description, "", "## Business Objectives", "", f"**CURRENT_OBJECTIVE:** {spec.current_objective.text}", "", f"**MODERNIZATION_OBJECTIVE:** {spec.modernization_objective.text}", "", "## Business Value", "", *(f"- **{item.classification}:** {item.text}" for item in spec.business_value), "", "## Primary Users / Actors", "", *(f"- **{item.name}:** {item.role}" for item in spec.actors), "" if spec.actors else spec.actor_evidence_limitation, "", "## Current Business Functionality", "", bullets([item.text for item in spec.current_business_functionality]), "", "## Business Workflows", ""]
    for workflow in spec.workflows:
        lines.extend([f"### {workflow.name}", "", f"- Trigger: {workflow.business_trigger}", f"- Steps: {'; '.join(workflow.business_steps)}", f"- Outcome: {workflow.expected_outcome}", f"- Supporting UI: {', '.join(workflow.supporting_ui) or 'Not identified'}", f"- API status: `{workflow.api_status}`", ""])
    lines.extend(["## Business Rules", "", *(f"- **{item.rule_id}:** {item.description}" for item in spec.business_rules), spec.no_business_rules_marker or "", "", "## Domain Concepts and Information", "", *(f"- **{item.name}:** {item.business_meaning} {item.role_in_feature}" for item in spec.domain_concepts), *[f"- {item.text}" for item in spec.information_involved], "", "## Dependencies", "", *(f"- **{item.dependency_type}:** {item.name} - {item.description}" for item in spec.dependencies), "", "## API Integration Profile", "", f"- PROVEN: {spec.api_integration.proven}", f"- UNRESOLVED: {spec.api_integration.unresolved}", f"- DYNAMIC: {spec.api_integration.dynamic}", f"- EXTERNAL: {spec.api_integration.external}", f"- NO_BACKEND_ROUTE: {spec.api_integration.no_backend_route}", *(f"- `{item.status}`: `{item.frontend_source}` -> `{item.api_contract}` -> `{item.backend_endpoint}`" for item in spec.api_integration.paths), f"- Limitation: {spec.api_integration.business_readable_limitation}", "", "## Current User Experience", "", bullets([item.text for item in spec.current_user_experience]), "", "## Current-State Limitations and Concerns", "", *[f"- **{item.classification}:** {item.text}" for item in [*spec.evidence_backed_limitations, *spec.modernization_concerns]], "", "## Modernization Scope", "", "### In Scope", "", bullets([item.text for item in spec.in_scope]), "", "### Out of Scope", "", bullets([item.text for item in spec.out_of_scope]), "", "## Assumptions", "", bullets([item.text for item in spec.assumptions]), "", "## Open Questions", "", *(f"- **{item.question_id}:** {item.question} Reason: {item.reason}" for item in spec.open_questions), "", "## Risks and Limitations", "", *[f"- **{item.classification}:** {item.text}" for item in spec.risks_and_limitations], "", "## MODERNIZATION_SUCCESS_INDICATORS", "", bullets([item.text for item in spec.success_indicators]), "", "## STORY_DECOMPOSITION_GUIDANCE", "", *(f"- **{item.boundary}:** {item.rationale} Workflows: {', '.join(item.workflows)}" for item in spec.story_decomposition_guidance), "", "## Technical Traceability", "", *(f"- `{item.source_path}:{item.line_start}` -> `{item.node_id}`" for item in spec.source_evidence), ""])
    return "\n".join(str(item) for item in lines) + "\n"


def validate_and_persist_business_features(feature_root: Path, output_root: Path, agent_result: Path) -> dict:
    approved = load_approved_features(feature_root)
    packages = build_business_feature_packages(approved)
    submission = BusinessFeatureReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    quality = _validate_submission(submission, approved, packages)
    readiness = "BUSINESS_FEATURES_READY_WITH_LIMITATIONS" if any(item.evidence_backed_limitations or item.open_questions for item in submission.business_features) else "BUSINESS_FEATURES_READY"
    project_id = approved["catalog"]["project_id"]
    run_id, destination = _run_path(output_root / "runs", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    catalog = BusinessFeatureCatalog(
        project_id=project_id, kg_run_id=submission.kg_run_id, application_understanding_run_id=submission.application_understanding_run_id,
        feature_run_id=submission.feature_run_id, business_feature_run_id=run_id, readiness=readiness,
        business_features=submission.business_features, limitations=["Inherited unresolved/dynamic API and incomplete-workflow evidence remains explicit."],
        quality_review=quality, next_action="GENERATE_JIRA_STYLE_STORIES",
        capability_coverage=approved["catalog"].get("capability_coverage", {}),
    )
    package_map, manifest_hash = _manifest(packages)
    _write_json(destination / "business-feature-catalog.json", catalog.model_dump(mode="json"))
    _write_json(destination / "business-feature-reasoning.json", submission.model_dump(mode="json"))
    _write_json(destination / "business-feature-validation.json", {"valid": True, **quality, "readiness": readiness})
    _write_json(destination / "capability-coverage.json", approved["catalog"].get("capability_coverage", {}))
    _write_json(destination / "business-feature-evidence-manifest.json", {"kg_run_id": submission.kg_run_id, "application_understanding_run_id": submission.application_understanding_run_id, "feature_run_id": submission.feature_run_id, "manifest_hash": manifest_hash, "hash_validation": "PASS", "packages": package_map})
    _write_json(destination / "open-questions.json", {"questions": [{"feature_id": spec.feature_id, **question.model_dump(mode="json")} for spec in submission.business_features for question in spec.open_questions]})
    _write_json(destination / "provenance.json", {"kg_run_id": submission.kg_run_id, "application_understanding_run_id": submission.application_understanding_run_id, "feature_run_id": submission.feature_run_id, "business_feature_run_id": run_id})
    _write_json(destination / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "external_llm_api_calls": 0, "evidence_packages": len(packages)})
    specifications = destination / "specifications"
    specifications.mkdir()
    for spec in submission.business_features:
        (specifications / f"{spec.feature_id}.md").write_text(_feature_markdown(spec), encoding="utf-8")
    summary = ["# Business Feature Catalog", "", f"- Readiness: `{readiness}`", f"- Business Feature run: `{run_id}`", f"- Approved Features enriched: {len(submission.business_features)}", f"- Open questions: {quality['open_questions']}", ""]
    for spec in submission.business_features:
        summary.extend([f"## {spec.feature_name}", "", spec.short_business_summary, "", f"- Feature ID: `{spec.feature_id}`", f"- Capabilities: {', '.join(spec.business_capabilities)}", f"- Workflows: {len(spec.workflows)}", f"- API: {spec.api_integration.proven} proven, {spec.api_integration.unresolved} unresolved, {spec.api_integration.dynamic} dynamic", f"- Open questions: {len(spec.open_questions)}", ""])
    (destination / "business-feature-summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    poc = next(item for item in submission.business_features if item.feature_id == approved["catalog"]["poc_selection"]["feature_ids"][0])
    (destination / "poc-business-feature.md").write_text(_feature_markdown(poc), encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "catalog": catalog, "quality": quality, "packages": packages}
