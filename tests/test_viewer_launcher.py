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
    assert "npx" not in script
    assert "github.com" not in script
    assert "http://" not in script and "https://" not in script
    assert "understand-anything-viewer.cmd" in script
    assert "install_understand_anything_viewer.ps1" in script


def test_installer_is_pinned_and_launcher_supports_any_safe_project_id():
    installer = (ROOT / "tools" / "install_understand_anything_viewer.ps1").read_text(encoding="utf-8")
    assert "https://github.com/Egonex-AI/Understand-Anything/releases/download/v2.9.0/understand-anything-viewer.tgz" in installer
    assert "understand-anything-viewer" in installer
    assert "healthclinic-dashboard" not in (ROOT / "tools" / "launch_understand_anything_viewer.ps1").read_text(encoding="utf-8")
