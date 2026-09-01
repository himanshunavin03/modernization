"""Deterministic framework detection from inventory metadata and JSON manifests."""
import json
from pathlib import Path

def detect_frameworks(source_root: Path, inventory: list[dict]) -> list[dict]:
    paths = {item["source_path"] for item in inventory}
    findings = []
    def add(name: str, evidence: str) -> None:
        findings.append({"framework": name, "source_path": evidence, "confidence": 1.0, "method": "deterministic-file-evidence"})
    if any(path.endswith((".cshtml", ".razor")) for path in paths): add("ASP.NET MVC/Razor", next(path for path in paths if path.endswith((".cshtml", ".razor"))))
    if any(path.endswith(".razor") for path in paths): add("Blazor", next(path for path in paths if path.endswith(".razor")))
    if any(path.endswith(".csproj") or path.endswith(".sln") for path in paths): add(".NET API", next(path for path in paths if path.endswith((".csproj", ".sln"))))
    for package_path in (item for item in inventory if item["source_path"].endswith(("package.json", "bower.json"))):
        try:
            package = json.loads((source_root / package_path["source_path"]).read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
        if "angular" in dependencies: add("AngularJS", package_path["source_path"])
        if "@angular/core" in dependencies: add("Angular", package_path["source_path"])
        if "typescript" in dependencies: add("TypeScript", package_path["source_path"])
    if any(path.endswith(".ts") for path in paths) and not any(item["framework"] == "TypeScript" for item in findings): add("TypeScript", next(path for path in paths if path.endswith(".ts")))
    return findings
