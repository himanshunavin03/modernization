from pathlib import Path

from polaris_modernization.tree_sitter_extractors import csharp


def test_csharp_syntax_does_not_classify_ordinary_types_as_angular_or_controllers(tmp_path):
    path = tmp_path / "Patient.cs"
    path.write_text("namespace Demo { class Patient { void Save() {} } class PatientsController { void Get() {} } }", encoding="utf-8")

    facts = csharp.extract(path, tmp_path, "hash", "demo")

    assert ("type", "Patient") in {(fact.kind, fact.name) for fact in facts}
    assert ("method", "Save") in {(fact.kind, fact.name) for fact in facts}
    assert ("controller", "PatientsController") in {(fact.kind, fact.name) for fact in facts}
    assert ("action", "Get") in {(fact.kind, fact.name) for fact in facts}
