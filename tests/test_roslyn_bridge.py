from pathlib import Path
from polaris_modernization.roslyn_bridge import enrich
from polaris_modernization.cli import analyze

ROOT=Path(__file__).resolve().parents[1]
def test_roslyn_unavailable_falls_back(monkeypatch,tmp_path):
    monkeypatch.setattr("polaris_modernization.roslyn_bridge.dotnet_executable",lambda:None)
    result=enrich(ROOT/"tests/fixtures/generic-graph","sample",tmp_path/"roslyn.json")
    assert result["project_id"]=="sample" and result["facts"]==[] and result["warnings"]
def test_enable_roslyn_writes_project_scoped_result(monkeypatch,tmp_path):
    monkeypatch.setattr("polaris_modernization.roslyn_bridge.shutil.which",lambda _:None)
    result=analyze(ROOT/"tests/fixtures/generic-graph","isolated","default",tmp_path,True)
    assert (result["output"]/"roslyn-semantic.json").is_file()
    assert result["roslyn"]["project_id"]=="isolated"
