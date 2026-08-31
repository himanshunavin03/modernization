"""Optional batch Roslyn adapter; LSP remains a documented future provider."""
import json, os, shutil, subprocess
from pathlib import Path
HELPER = Path(__file__).resolve().parents[2] / "tools" / "Polaris.RoslynAnalyzer" / "Polaris.RoslynAnalyzer.csproj"
def dotnet_executable() -> str | None:
    return shutil.which("dotnet") or next((str(path) for path in (Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "dotnet" / "dotnet.exe", Path(r"C:\Program Files\dotnet\dotnet.exe")) if path.is_file()), None)
def enrich(source_root: Path, project_id: str, output: Path) -> dict:
    csharp = list(source_root.rglob("*.cs"))
    if not csharp: return {"project_id":project_id,"facts":[],"warnings":[{"message":"No C# files found."}]}
    dotnet = dotnet_executable()
    if not dotnet: return {"project_id":project_id,"facts":[],"warnings":[{"message":"dotnet SDK unavailable; Roslyn enrichment skipped."}]}
    environment = os.environ.copy()
    dotnet_home = str(Path(dotnet).parent)
    environment.setdefault("DOTNET_ROOT", dotnet_home)
    environment["PATH"] = dotnet_home + os.pathsep + environment.get("PATH", "")
    subprocess.run([dotnet,"run","--project",str(HELPER),"--","--source-root",str(source_root),"--project-id",project_id,"--output",str(output)],check=True,env=environment)
    return json.loads(output.read_text(encoding="utf-8"))
