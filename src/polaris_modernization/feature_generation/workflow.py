"""Provider-free Feature preparation, deterministic validation, and persistence."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil

from polaris_modernization.feature_generation.models import FeatureCatalog, FeatureReasoningSubmission
from polaris_modernization.feature_generation.retrieval import COLLECTIONS, build_feature_evidence_packages, load_approved_application_understanding


class UnsupportedFeatureClaimsError(ValueError):
    """A Feature submission is stale, malformed, or unsupported by approved evidence."""


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


def prepare_feature_generation(application_understanding_root: Path, output_root: Path) -> dict:
    approved = load_approved_application_understanding(application_understanding_root)
    packages = build_feature_evidence_packages(approved)
    project_id = approved["understanding"]["project_id"]
    run_id, destination = _run_path(output_root / "prepared", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    package_manifest, manifest_hash = _manifest(packages)
    _write_json(destination / "feature-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write_json(destination / "feature-evidence-package-manifest.json", {
        "kg_run_id": approved["kg_run_id"], "application_understanding_run_id": approved["run_id"],
        "manifest_hash": manifest_hash, "packages": package_manifest,
    })
    _write_json(destination / "feature-reasoning-schema.json", FeatureReasoningSubmission.model_json_schema())
    (destination / "agent-instructions.md").write_text(
        "# Feature Reasoning Instructions\n\nRead only the Feature evidence packages and schema. Produce business Features, not technical artifacts. "
        "Reuse exact upstream object names and evidence. Preserve each workflow API status exactly; only upstream `PROVEN` may remain `PROVEN`. "
        "Bind the exact KG run, Application Understanding run, and package manifest hash. Select both approved Dashboard surfaces for the POC and do not generate Stories.\n",
        encoding="utf-8",
    )
    _write_json(destination / "preparation.json", {
        "project_id": project_id, "kg_run_id": approved["kg_run_id"],
        "application_understanding_run_id": approved["run_id"], "feature_evidence_packages": len(packages),
        "evidence_package_manifest_hash": manifest_hash, "external_llm_api_calls": 0,
    })
    return {"run_id": run_id, "path": destination, "approved": approved, "packages": packages}


def _object_maps(understanding: dict) -> dict[str, dict[str, dict]]:
    return {
        "module": {item["name"]: item for item in understanding["business_modules"]},
        "capability": {item["name"]: item for item in understanding["business_capabilities"]},
        "workflow": {item["name"]: item for item in understanding["user_workflows"]},
        "ui_surface": {item["name"]: item for item in understanding["ui_surfaces"]},
        "domain_concept": {item["name"]: item for item in understanding["domain_concepts"]},
        "business_rule": {item["name"]: item for item in understanding["business_rules"]},
        "dependency": {item["name"]: item for item in understanding["dependencies"]},
    }


def _package_scope(packages: list, package_ids: list[str]) -> tuple[set[tuple], set[str], set[tuple[str, str]]]:
    selected = [item for item in packages if item.package_id in package_ids]
    evidence = {(ref.node_id, ref.source_path, ref.line_start, ref.line_end, ref.provenance) for item in selected for ref in item.evidence}
    nodes = {ref.node_id for item in selected for ref in item.evidence}
    object_types = {
        "modules": "module", "capabilities": "capability", "workflows": "workflow",
        "ui_surfaces": "ui_surface", "domain_concepts": "domain_concept",
        "business_rules": "business_rule", "dependencies": "dependency",
    }
    objects = {(object_types[kind], value["name"]) for item in selected for kind, values in item.objects.items() for value in values}
    return evidence, nodes, objects


def _validate_submission(submission: FeatureReasoningSubmission, approved: dict, packages: list) -> dict:
    package_manifest, manifest_hash = _manifest(packages)
    if submission.kg_run_id != approved["kg_run_id"] or submission.application_understanding_run_id != approved["run_id"]:
        raise UnsupportedFeatureClaimsError("Feature submission references stale upstream runs.")
    if submission.evidence_package_manifest_hash != manifest_hash:
        raise UnsupportedFeatureClaimsError("Feature evidence package manifest hash is stale.")
    if len({item.feature_id for item in submission.features}) != len(submission.features):
        raise UnsupportedFeatureClaimsError("Duplicate Feature IDs are not allowed.")
    maps = _object_maps(approved["understanding"])
    valid_package_ids = set(package_manifest)
    for feature in submission.features:
        if not re.fullmatch(r"feature-[a-z0-9-]+", feature.feature_id) or not feature.title.strip() or not feature.business_outcome.strip():
            raise UnsupportedFeatureClaimsError("Features require a stable ID, title, and business outcome.")
        if not feature.workflows or not feature.source_evidence or not feature.kg_evidence or not feature.application_understanding_evidence:
            raise UnsupportedFeatureClaimsError("Feature traceability is incomplete.")
        if not feature.evidence_package_ids or len(set(feature.evidence_package_ids)) != len(feature.evidence_package_ids) or not set(feature.evidence_package_ids) <= valid_package_ids:
            raise UnsupportedFeatureClaimsError("Feature package references are missing, duplicated, or invalid.")
        evidence, nodes, package_objects = _package_scope(packages, feature.evidence_package_ids)
        references = {
            "module": [feature.module], "capability": feature.business_capabilities,
            "workflow": feature.workflows, "ui_surface": feature.ui_surfaces,
            "domain_concept": feature.domain_concepts, "business_rule": feature.business_rules,
            "dependency": feature.dependencies,
        }
        for kind, names in references.items():
            if any(name not in maps[kind] for name in names):
                raise UnsupportedFeatureClaimsError(f"Feature references an unknown {kind}.")
            if any((kind, name) not in package_objects for name in names):
                raise UnsupportedFeatureClaimsError(f"Feature references a {kind} outside its selected evidence packages.")
        for reference in feature.application_understanding_evidence:
            if reference.name not in maps[reference.object_type] or (reference.object_type, reference.name) not in package_objects:
                raise UnsupportedFeatureClaimsError("Feature references unsupported Application Understanding evidence.")
        for reference in feature.source_evidence:
            key = (reference.node_id, reference.source_path, reference.line_start, reference.line_end, reference.provenance)
            if key not in evidence:
                raise UnsupportedFeatureClaimsError("Feature references unsupported source evidence.")
        if any(node_id not in nodes for node_id in feature.kg_evidence):
            raise UnsupportedFeatureClaimsError("Feature references unsupported KG evidence.")
        for contract in feature.api_contracts:
            workflow = maps["workflow"].get(contract.workflow)
            if workflow is None or contract.workflow not in feature.workflows or contract.status != workflow["backend_mapping"]:
                raise UnsupportedFeatureClaimsError("Feature changed or invented an API mapping status.")
    feature_ids = {item.feature_id for item in submission.features}
    poc = submission.poc_selection
    if not set(poc.feature_ids) <= feature_ids or poc.razor_feature_id not in feature_ids or poc.angularjs_feature_id not in feature_ids:
        raise UnsupportedFeatureClaimsError("POC selection references an unknown Feature.")
    understanding = approved["understanding"]
    if poc.razor_surface != understanding["best_razor_demo_candidate"] or poc.angularjs_surface != understanding["best_angular_demo_candidate"]:
        raise UnsupportedFeatureClaimsError("POC selection changed the approved modernization candidates.")
    covered_capabilities = {name for feature in submission.features for name in feature.business_capabilities}
    covered_workflows = {name for feature in submission.features for name in feature.workflows}
    titles = [re.sub(r"\W+", " ", item.title.lower()).strip() for item in submission.features]
    technical_titles = [item.title for item in submission.features if re.search(r"\b(controller|service|endpoint|dto|class|file)\b", item.title, re.I)]
    return {
        "package_hash_validation": "PASS", "provenance_validation": "PASS", "feature_validation": "PASS",
        "unsupported_feature_claims_rejected": 0,
        "duplicate_features": len(titles) - len(set(titles)), "untraceable_features": 0,
        "technical_feature_titles": technical_titles,
        "overly_broad_features": [item.feature_id for item in submission.features if len(item.workflows) > 10],
        "overly_granular_features": [item.feature_id for item in submission.features if len(item.workflows) == 1 and not item.business_rules and not item.domain_concepts],
        "capabilities_covered": sorted(covered_capabilities),
        "uncovered_capabilities": sorted(set(maps["capability"]) - covered_capabilities),
        "workflows_covered": sorted(covered_workflows),
        "uncovered_workflows": sorted(set(maps["workflow"]) - covered_workflows),
    }


def validate_and_persist_features(application_understanding_root: Path, output_root: Path, agent_result: Path) -> dict:
    approved = load_approved_application_understanding(application_understanding_root)
    packages = build_feature_evidence_packages(approved)
    submission = FeatureReasoningSubmission.model_validate_json(agent_result.read_text(encoding="utf-8"))
    quality = _validate_submission(submission, approved, packages)
    has_limitations = any(feature.limitations or any(contract.status != "PROVEN" for contract in feature.api_contracts) for feature in submission.features)
    readiness = "FEATURES_READY_WITH_LIMITATIONS" if has_limitations or quality["uncovered_workflows"] else "FEATURES_READY"
    project_id = approved["understanding"]["project_id"]
    run_id, destination = _run_path(output_root / "runs", project_id)
    destination.mkdir(parents=True, exist_ok=False)
    limitations = [
        "Unresolved, dynamic, external, and no-backend-route API limitations are inherited unchanged from the approved Application Understanding.",
        f"{len(quality['uncovered_workflows'])} upstream workflows are not promoted into business Features and remain explicitly uncovered.",
    ]
    catalog = FeatureCatalog(
        project_id=project_id, kg_run_id=approved["kg_run_id"], application_understanding_run_id=approved["run_id"],
        feature_run_id=run_id, readiness=readiness, features=submission.features,
        poc_selection=submission.poc_selection, quality_review=quality, limitations=limitations,
        next_action="GENERATE_STORIES" if readiness != "FEATURES_NOT_READY" else "CORRECT_FEATURE_EVIDENCE",
    )
    package_manifest, manifest_hash = _manifest(packages)
    _write_json(destination / "feature-catalog.json", catalog.model_dump(mode="json"))
    _write_json(destination / "feature-reasoning.json", submission.model_dump(mode="json"))
    _write_json(destination / "feature-evidence-packages.json", [item.model_dump(mode="json") for item in packages])
    _write_json(destination / "feature-evidence-package-manifest.json", {
        "kg_run_id": approved["kg_run_id"], "application_understanding_run_id": approved["run_id"],
        "manifest_hash": manifest_hash, "hash_validation": "PASS", "packages": package_manifest,
    })
    _write_json(destination / "feature-validation.json", {
        "valid": True, **quality, "readiness": readiness, "total_features": len(submission.features),
        "total_capabilities": len(approved["understanding"]["business_capabilities"]),
        "total_workflows": len(approved["understanding"]["user_workflows"]),
    })
    _write_json(destination / "poc-feature-selection.json", submission.poc_selection.model_dump(mode="json"))
    _write_json(destination / "provenance.json", {
        "kg_run_id": approved["kg_run_id"], "application_understanding_run_id": approved["run_id"],
        "feature_run_id": run_id, "source": "APPROVED_APPLICATION_UNDERSTANDING",
    })
    _write_json(destination / "token-usage.json", {"reasoning_mode": "INTERACTIVE_AGENT_MODE", "external_llm_api_calls": 0, "feature_evidence_packages": len(packages)})
    lines = [
        "# Evidence-Backed Modernization Features", "", f"- Readiness: `{readiness}`",
        f"- KG run: `{approved['kg_run_id']}`", f"- Application Understanding run: `{approved['run_id']}`",
        f"- Feature run: `{run_id}`", f"- Features: {len(submission.features)}", "",
    ]
    for feature in submission.features:
        lines.extend([f"## {feature.feature_id}: {feature.title}", "", feature.business_outcome, "", f"- Module: {feature.module}", f"- Capabilities: {', '.join(feature.business_capabilities)}", f"- Priority: `{feature.modernization_priority}`", f"- API statuses: {', '.join(sorted({item.status for item in feature.api_contracts})) or 'NOT_APPLICABLE'}", f"- Workflows: {', '.join(feature.workflows)}", ""])
    lines.extend(["## POC Selection", "", f"- Feature IDs: {', '.join(submission.poc_selection.feature_ids)}", f"- Razor: `{submission.poc_selection.razor_surface}`", f"- AngularJS: `{submission.poc_selection.angularjs_surface}`", "", "## Uncovered Workflows", "", *(f"- {item}" for item in quality["uncovered_workflows"])])
    (destination / "feature-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    latest = output_root / "latest"
    if latest.exists():
        shutil.rmtree(latest)
    shutil.copytree(destination, latest)
    return {"run_id": run_id, "path": destination, "catalog": catalog, "packages": packages, "quality": quality}
