"""Optional batch Roslyn adapter; LSP remains a documented future provider."""
import json, shutil, subprocess
from pathlib import Path
HELPER = Path(__file__).resolve().parents[2] / "tools" / "Polaris.RoslynAnalyzer" / "Polaris.RoslynAnalyzer.csproj"
def enrich(source_root: Path, project_id: str, output: Path) -> dict:
    csharp = list(source_root.rglob("*.cs"))
    if not csharp: return {"project_id":project_id,"facts":[],"warnings":[{"message":"No C# files found."}]}
    if not shutil.which("dotnet"): return {"project_id":project_id,"facts":[],"warnings":[{"message":"dotnet SDK unavailable; Roslyn enrichment skipped."}]}
    subprocess.run(["dotnet","run","--project",str(HELPER),"--","--source-root",str(source_root),"--project-id",project_id,"--output",str(output)],check=True)
    return json.loads(output.read_text(encoding="utf-8"))
