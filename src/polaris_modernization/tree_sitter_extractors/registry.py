"""Language adapter registry; unsupported types are inventoried but not guessed."""
from polaris_modernization.tree_sitter_extractors import csharp, html, javascript

EXTRACTORS = {".cs": csharp, ".cshtml": html, ".razor": html, ".html": html, ".js": javascript}

def extractor_for(path):
    return EXTRACTORS.get(path.suffix.lower())
