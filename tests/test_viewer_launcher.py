from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_launcher_requires_safe_parameters_and_uses_only_artifact_paths():
    script = (ROOT / "tools" / "launch_understand_anything_viewer.ps1").read_text(encoding="utf-8")
    assert "[Parameter(Mandatory)]" in script
    assert "[ValidatePattern('^[a-z0-9][a-z0-9-]{0,62}$')]" in script
    assert "knowledge-graph.json" in script
    assert "visualization" in script
    assert "source/" not in script
    assert "$env:UNDERSTAND_ACCESS_TOKEN = $AccessToken" in script
    assert "viewer.tgz" in script
