"""Load generic or focused analysis profiles without application-specific code."""
from pathlib import Path
import yaml

PROFILE_DIRECTORY = Path(__file__).resolve().parents[2] / "config" / "profiles"

def load_profile(profile: str) -> dict:
    candidate = Path(profile)
    path = candidate if candidate.is_file() else PROFILE_DIRECTORY / f"{profile.removesuffix('.yaml')}.yaml"
    if not path.is_file():
        raise ValueError(f"Profile not found: {profile}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    data["profile_path"] = str(path)
    return data

def merge_profiles(default: dict, selected: dict) -> dict:
    merged = dict(default)
    merged.update({key: value for key, value in selected.items() if key != "supported_extensions"})
    return merged
