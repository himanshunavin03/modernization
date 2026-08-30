from pathlib import Path

from polaris_modernization.config import load_scope
from polaris_modernization.source_inventory import build_inventory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "source" / "HealthClinic.biz"


def test_dashboard_inventory_contains_approved_dashboard_files():
    inventory = build_inventory(SOURCE_ROOT, load_scope("dashboard"))
    paths = {item["source_path"] for item in inventory}

    assert "src/MyHealth.Web/Views/Dashboard/Index.cshtml" in paths
    assert "src/MyHealth.Web/Controllers/DashboardController.cs" in paths
    assert "src/MyHealth.Web/content/app/app.module.js" in paths
    assert all(item["source_hash"] for item in inventory)
