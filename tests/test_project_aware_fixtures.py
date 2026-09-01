from pathlib import Path

from polaris_modernization.roslyn_bridge import enrich


ROOT = Path(__file__).resolve().parent / "fixtures"


def analyze_fixture(name, tmp_path):
    return enrich(ROOT / name, name, tmp_path / f"{name}.json")


def test_multi_project_workspace_uses_only_compiler_proven_context(tmp_path):
    result = analyze_fixture("roslyn-multiproject", tmp_path)
    facts = result["facts"]
    invocations = [fact for fact in facts if fact["kind"] == "invocation"]

    assert result["semantic_coverage"] == {"compiler_proven_files": 3, "synthetic_fallback_files": 0, "structural_only_files": 0}
    assert all(fact["properties"]["analysis_mode"] == "PROJECT_COMPILATION" for fact in facts)
    assert all(fact["evidence"]["confidence"] == 1.0 for fact in invocations)
    assert any("Fixture.Data.IStore.Read" in fact["properties"]["target_identity"] for fact in invocations)
    assert any("Fixture.Business.Service.Load" in fact["properties"]["target_identity"] for fact in invocations)
    assert any(fact["properties"].get("invocation_kind") == "constructor" and "Fixture.Business.Service.Service" in fact["properties"]["target_identity"] for fact in invocations)
    assert any("Fixture.Business.BaseService.Format" in fact["properties"]["target_identity"] for fact in invocations)
    assert any("Fixture.Data.StoreExtensions.Identity" in fact["properties"]["target_identity"] for fact in invocations)
    assert any(fact["properties"].get("usage") == "parameter" for fact in facts if fact["kind"] == "type_reference")
    assert any(fact["properties"].get("usage") == "return" for fact in facts if fact["kind"] == "type_reference")
    identities = [fact["properties"].get("identity") for fact in facts if fact["kind"] in {"type", "method"}]
    identities = [identity for identity in identities if identity]
    assert len(identities) == len(set(identities))


def test_failed_project_keeps_project_facts_and_narrow_synthetic_fallback(tmp_path):
    result = analyze_fixture("roslyn-fallback", tmp_path)
    facts = result["facts"]
    fallback = [fact for fact in facts if fact["properties"].get("analysis_mode") == "SYNTHETIC_FALLBACK"]
    project = [fact for fact in facts if fact["properties"].get("analysis_mode") in {"PROJECT_COMPILATION", "PARTIAL_PROJECT_COMPILATION"}]

    assert result["semantic_coverage"]["compiler_proven_files"] == 2
    assert result["semantic_coverage"]["synthetic_fallback_files"] == 1
    assert fallback and project
    assert all(fact["evidence"]["confidence"] <= 0.6 for fact in fallback if fact["evidence"]["resolution_status"] == "proven")
    assert any(item["category"] == "PROJECT_LOAD_FAILURE" for item in result["warnings"])
    unresolved = result["unresolved_analysis"]
    assert unresolved["totals"]["PROJECT_LOAD_FAILURE"] >= 1
    assert unresolved["totals"]["COMPILATION_ERROR"] >= 1
    assert unresolved["total_unresolved_occurrences"] >= unresolved["unique_unresolved_diagnostics"]
    assert not any(fact["evidence"]["resolution_status"] == "proven" and fact["properties"].get("target_name") == "MissingType.Build" for fact in facts)


def test_inaccessible_invocation_is_classified_without_a_proven_target(tmp_path):
    result = analyze_fixture("roslyn-inaccessible", tmp_path)
    inaccessible = [fact for fact in result["facts"] if fact["kind"] == "invocation" and fact["properties"].get("unresolved_classification") == "INACCESSIBLE"]

    assert len(inaccessible) == 1
    fact = inaccessible[0]
    assert fact["evidence"]["resolution_status"] == "unresolved"
    assert fact["evidence"]["confidence"] == 0.0
    assert fact["properties"]["candidate_reason"] == "Inaccessible"
    assert fact["properties"]["candidate_symbols"]
    assert result["unresolved_analysis"]["totals"]["INACCESSIBLE"] == 1
    assert not [item for item in result["facts"] if item["kind"] == "invocation" and item["evidence"]["resolution_status"] == "proven" and item["name"] == "Hidden"]
