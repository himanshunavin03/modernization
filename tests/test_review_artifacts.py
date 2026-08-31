import json

from polaris_modernization.review_artifacts import preserve_completed_run, validate_run_output


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def complete_run(path):
    path.mkdir()
    graph = {"nodes": [{"id": "n", "label": "File", "evidence": [{"source_path": "a.cs"}]}], "edges": [], "warnings": []}
    for name, value in {
        "knowledge-graph.json": graph, "facts.json": {"facts": []}, "source-inventory.json": {"files": []},
        "framework-detection.json": {}, "graph-run-status.json": {"neo4j": {"status": "skipped"}},
        "roslyn-semantic.json": {"facts": []}, "roslyn-semantic-all.json": {"facts": []},
    }.items(): write_json(path / name, value)
    for name in ("graph-run-summary.md", "analysis-summary.md"): (path / name).write_text("summary", encoding="utf-8")


def test_validated_run_is_copied_raw_to_latest_and_timestamped_run(tmp_path):
    run = tmp_path / "raw"; complete_run(run)
    result = preserve_completed_run(run, "demo-app", enable_roslyn=True, archive_root=tmp_path / "archive")

    assert result["validation"]["valid"] is True
    assert (tmp_path / "archive" / "latest" / "knowledge-graph.json").read_bytes() == (run / "knowledge-graph.json").read_bytes()
    assert (tmp_path / "archive" / "runs" / result["run_id"] / "review-metadata.json").is_file()


def test_secret_finding_blocks_archive(tmp_path):
    run = tmp_path / "raw"; complete_run(run)
    (run / "facts.json").write_text('{"password":"not-safe-value"}', encoding="utf-8")
    report = validate_run_output(run, enable_roslyn=True)

    assert report["valid"] is False
    assert report["secret_scan_findings"]
