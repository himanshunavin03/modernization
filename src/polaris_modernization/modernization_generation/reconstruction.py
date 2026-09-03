"""Deterministic normalization of the real HealthClinic Dashboard UI."""
from __future__ import annotations

from pathlib import Path
import re

from .models import ExistingUiSpecification


RAZOR_FILES = [
    "src/MyHealth.Web/Views/Dashboard/Index.cshtml",
    "src/MyHealth.Web/Views/Dashboard/_Header.cshtml",
    "src/MyHealth.Web/Views/Dashboard/_LeftMenu.cshtml",
    "src/MyHealth.Web/Views/Dashboard/_Content.cshtml",
    "src/MyHealth.Web/Views/Dashboard/_Footer.cshtml",
]
ANGULARJS_FILES = [
    "src/MyHealth.Web/content/app/app.module.js",
    "src/MyHealth.Web/content/app/components/dashboard/dashboard.module.js",
    "src/MyHealth.Web/content/app/components/dashboard/controllers/dashboardController.js",
    "src/MyHealth.Web/content/app/components/dashboard/services/dashboardService.js",
    "src/MyHealth.Web/content/app/components/dashboard/directives/MHChartDirective.js",
    "src/MyHealth.Web/content/app/components/dashboard/views/main.html",
]
SHARED_UI_FILES = [
    "src/MyHealth.Web/content/app/components/shared/directives/headerBar/headerBarTemplate.html",
    "src/MyHealth.Web/content/app/components/shared/directives/leftMenu/leftMenuTemplate.html",
]
STYLE_FILES = [
    "src/MyHealth.Web/content/styles/base/_variables.scss",
    "src/MyHealth.Web/content/styles/private/base/_general.scss",
    "src/MyHealth.Web/content/styles/private/components/_summary.scss",
    "src/MyHealth.Web/content/styles/private/components/_charts.scss",
    "src/MyHealth.Web/content/styles/private/layout/_header.scss",
    "src/MyHealth.Web/content/styles/private/layout/_menu.scss",
    "src/MyHealth.Web/content/styles/private/layout/_main.scss",
    "src/MyHealth.Web/content/styles/private/layout/_footer.scss",
]
ASSET_FILES = [
    "src/MyHealth.Web/content/images/private/logo_private_area.png",
    "src/MyHealth.Web/content/images/private/logo_private_area_footer.png",
    "src/MyHealth.Web/content/images/dashboard/arrow_01.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_01.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_01_snap.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_02.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_02_snap.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_03.png",
    "src/MyHealth.Web/content/images/dashboard/summary/bg_graph_03_snap.png",
]


def _read_required(source_root: Path, relative: str, markers: tuple[str, ...]) -> str:
    path = source_root / relative
    if not path.is_file():
        raise ValueError(f"Required existing UI source is missing: {relative}")
    content = path.read_text(encoding="utf-8-sig")
    missing = [marker for marker in markers if marker not in content]
    if missing:
        raise ValueError(f"Existing UI source {relative} is missing expected evidence: {missing}")
    return content


def reconstruct_existing_ui(source_root: Path, feature_id: str) -> ExistingUiSpecification:
    _read_required(source_root, RAZOR_FILES[0], ("_Header", "_LeftMenu", "_Content", "_Footer"))
    _read_required(source_root, ANGULARJS_FILES[0], ("url: '/dashboard'", "dashboardController", "views/main.html"))
    _read_required(source_root, ANGULARJS_FILES[2], ("incomesExpensesYear", "patientsYear", "getSummary", "getExpenses", "getPatients"))
    service = _read_required(source_root, ANGULARJS_FILES[3], tuple(endpoint for endpoint in ("/api/users/current/tenant", "/api/reports/clinicsummary", "/api/reports/expenses/", "/api/reports/patients/")))
    template = _read_required(source_root, ANGULARJS_FILES[5], ("NEW PATIENTS", "MONTH BENEFITS", "ANNUAL BENEFITS", "INCOMES AND EXPENSES", "PATIENT VISITS"))
    for relative in [*RAZOR_FILES, *ANGULARJS_FILES, *SHARED_UI_FILES, *STYLE_FILES, *ASSET_FILES]:
        if not (source_root / relative).is_file():
            raise ValueError(f"Required existing UI evidence is missing: {relative}")

    surfaces = [
        *[{"id": f"UI-RZ-{index:02d}", "kind": "RAZOR", "name": Path(path).stem, "source_path": path} for index, path in enumerate(RAZOR_FILES, 1)],
        *[{"id": f"UI-NG1-{index:02d}", "kind": "ANGULARJS", "name": Path(path).name, "source_path": path} for index, path in enumerate(ANGULARJS_FILES, 1)],
        *[{"id": f"UI-SH-{index:02d}", "kind": "SHARED_UI", "name": Path(path).name, "source_path": path} for index, path in enumerate(SHARED_UI_FILES, 1)],
    ]
    regions = [
        {"id": "UI-REG-01", "name": "Private application header", "source_ref": "UI-SH-01", "target": "PrivateShellComponent"},
        {"id": "UI-REG-02", "name": "Collapsible navigation drawer", "source_ref": "UI-SH-02", "target": "PrivateShellComponent"},
        {"id": "UI-REG-03", "name": "Dashboard route outlet and loading overlay", "source_ref": "UI-RZ-04", "target": "PrivateShellComponent"},
        {"id": "UI-REG-04", "name": "Clinic summary card row", "source_ref": "UI-NG1-06", "target": "DashboardFeatureComponent"},
        {"id": "UI-REG-05", "name": "New patients summary", "source_ref": "UI-NG1-06", "target": "SummaryCardComponent"},
        {"id": "UI-REG-06", "name": "Month benefits summary", "source_ref": "UI-NG1-06", "target": "SummaryCardComponent"},
        {"id": "UI-REG-07", "name": "Annual benefits summary", "source_ref": "UI-NG1-06", "target": "SummaryCardComponent"},
        {"id": "UI-REG-08", "name": "Income and expenses yearly chart", "source_ref": "UI-NG1-06", "target": "DashboardChartComponent"},
        {"id": "UI-REG-09", "name": "Patient visits yearly chart", "source_ref": "UI-NG1-06", "target": "DashboardChartComponent"},
        {"id": "UI-REG-10", "name": "Private application footer", "source_ref": "UI-RZ-05", "target": "PrivateShellComponent"},
    ]
    controls = [
        {"id": "UI-CTL-01", "name": "Menu toggle", "kind": "BUTTON", "target": "PrivateShellComponent"},
        {"id": "UI-CTL-02", "name": "Dashboard navigation link", "kind": "LINK", "target": "PrivateShellComponent"},
        {"id": "UI-CTL-03", "name": "Previous income and expense year", "kind": "BUTTON", "target": "YearNavigatorComponent"},
        {"id": "UI-CTL-04", "name": "Next income and expense year", "kind": "BUTTON", "target": "YearNavigatorComponent"},
        {"id": "UI-CTL-05", "name": "Previous patient year", "kind": "BUTTON", "target": "YearNavigatorComponent"},
        {"id": "UI-CTL-06", "name": "Next patient year", "kind": "BUTTON", "target": "YearNavigatorComponent"},
    ]
    labels = ["MENU", "Dashboard", "NEW PATIENTS", "MONTH BENEFITS", "ANNUAL BENEFITS", "INCOMES AND EXPENSES", "PATIENT VISITS", "Terms", "Privacy", "Contact", "Sitemap"]
    visible_text = [{"text": label, "source_path": ANGULARJS_FILES[5] if label not in {"MENU", "Dashboard", "Terms", "Privacy", "Contact", "Sitemap"} else RAZOR_FILES[2] if label == "MENU" else RAZOR_FILES[4] if label in {"Terms", "Privacy", "Contact", "Sitemap"} else "src/MyHealth.Web/content/app/components/shared/directives/leftMenu/leftMenuTemplate.html"} for label in labels]
    navigation = [{"old_route": "/dashboard", "new_route": "/dashboard", "source_path": ANGULARJS_FILES[0], "target": "DASHBOARD_ROUTES"}]
    interactions = [
        {"id": "UI-INT-01", "behavior": "Dashboard route loads the main Dashboard view.", "source_path": ANGULARJS_FILES[0]},
        {"id": "UI-INT-02", "behavior": "Each report year can decrement independently and cannot increment beyond the current year.", "source_path": ANGULARJS_FILES[2]},
        {"id": "UI-INT-03", "behavior": "Clinic summary loads for current tenant context.", "source_path": ANGULARJS_FILES[3]},
        {"id": "UI-INT-04", "behavior": "Income, expense, and patient series are normalized into twelve monthly values.", "source_path": ANGULARJS_FILES[2]},
    ]
    layouts = [
        {"name": "Desktop summary grid", "relationship": "Three equal columns with 20px gutters", "source_path": STYLE_FILES[2]},
        {"name": "Tablet summary stack", "relationship": "Summary cards stack with 20px bottom spacing", "source_path": STYLE_FILES[2]},
        {"name": "Chart panels", "relationship": "White bordered panels with title, right-aligned year filter, chart, and optional legend", "source_path": STYLE_FILES[3]},
        {"name": "Private shell", "relationship": "Fixed dark header, off-canvas menu, centered content, dark footer", "source_path": STYLE_FILES[4]},
    ]
    styles = [
        {"token": "private-shell", "value": "#1d1e2a", "source_path": STYLE_FILES[0]},
        {"token": "summary-patients", "value": "#00d8cc", "source_path": STYLE_FILES[0]},
        {"token": "summary-month", "value": "#71717f", "source_path": STYLE_FILES[0]},
        {"token": "summary-annual", "value": "#b8b8b9", "source_path": STYLE_FILES[0]},
        {"token": "accent", "value": "#ff1770", "source_path": STYLE_FILES[0]},
        {"token": "content-background", "value": "#f0f0f0", "source_path": STYLE_FILES[0]},
        {"token": "body-font", "value": "Raleway", "source_path": "src/MyHealth.Web/content/styles/base/_fonts.scss"},
        {"token": "numeric-font", "value": "Roboto", "source_path": STYLE_FILES[2]},
    ]
    classes = sorted({name for value in re.findall(r'class="([^"]+)"', template) for name in value.split()})
    css_classes = [{"name": name, "source_path": ANGULARJS_FILES[5]} for name in classes]
    data_bindings = [
        {"binding": name, "target_model": model, "source_path": ANGULARJS_FILES[5]}
        for name, model in (("summary.NewPatients", "ClinicSummary.NewPatients"), ("summary.NewPatientsVariation", "ClinicSummary.NewPatientsVariation"), ("summary.MonthProfit", "ClinicSummary.MonthProfit"), ("summary.MonthProfitVariation", "ClinicSummary.MonthProfitVariation"), ("summary.AnualProfit", "ClinicSummary.AnualProfit"), ("summary.AnualProfitVariation", "ClinicSummary.AnualProfitVariation"), ("elem.Expenses", "ExpensesSummary.Expenses"), ("elem.Incomes", "ExpensesSummary.Incomes"), ("elem.PatientsCount", "PatientsSummary.PatientsCount"))
    ]
    api_relationships = [
        {"api_id": "API-01", "method": "GET", "endpoint": "/api/users/current/tenant", "source_path": ANGULARJS_FILES[3]},
        {"api_id": "API-02", "method": "GET", "endpoint": "/api/reports/expenses/{year}", "source_path": ANGULARJS_FILES[3]},
        {"api_id": "API-03", "method": "GET", "endpoint": "/api/reports/patients/{year}", "source_path": ANGULARJS_FILES[3]},
        {"api_id": "API-04", "method": "GET", "endpoint": "/api/reports/clinicsummary", "source_path": ANGULARJS_FILES[3]},
    ]
    assert all(item["endpoint"].replace("{year}", "") in service for item in api_relationships)
    responsive = [
        {"behavior": "Summary cards use three columns at 992px and above.", "source_path": STYLE_FILES[2]},
        {"behavior": "Summary cards stack at tablet widths and below.", "source_path": STYLE_FILES[2]},
        {"behavior": "Chart rendering is responsive to its container.", "source_path": ANGULARJS_FILES[4]},
    ]
    assets = [{"source_path": path, "target_path": "apps/healthclinic-web/public/assets/" + path.split("/content/images/", 1)[1], "reuse_status": "REUSED_EXISTING_UI_ASSET"} for path in ASSET_FILES]
    shared = [
        {"name": "Private shell header", "source_path": SHARED_UI_FILES[0], "target": "PrivateShellComponent"},
        {"name": "Navigation drawer", "source_path": SHARED_UI_FILES[1], "target": "PrivateShellComponent"},
        {"name": "Loading overlay", "source_path": RAZOR_FILES[3], "target": "PrivateShellComponent"},
        {"name": "Footer", "source_path": RAZOR_FILES[4], "target": "PrivateShellComponent"},
    ]
    unresolved = [
        {"status": "UI_RECONSTRUCTION_CLARIFICATION", "item": "Header identity and broader navigation", "detail": "The current user's display name and non-Dashboard navigation authorization depend on APIs outside the approved hero contract; the generated hero shell does not fabricate them."},
        {"status": "UI_RECONSTRUCTION_CLARIFICATION", "item": "Legacy chart tooltip animation", "detail": "The generated accessible SVG presentation preserves series, months, colors, and hierarchy without copying obsolete Chart.js/jQuery tooltip mechanics; exact hover animation awaits visual review."},
        {"status": "UI_RECONSTRUCTION_CLARIFICATION", "item": "Legacy icon font glyphs", "detail": "Hero controls use accessible text symbols instead of copying the application-wide icon font; exact glyph equivalence awaits visual review."},
    ]
    return ExistingUiSpecification(
        feature_id=feature_id, surfaces=surfaces, regions=regions, controls=controls,
        visible_text=visible_text, navigation=navigation, interactions=interactions, layouts=layouts,
        styles=styles, css_classes=css_classes, assets=assets, data_bindings=data_bindings,
        api_relationships=api_relationships, responsive_behavior=responsive, shared_elements=shared,
        unresolved_visual_details=unresolved,
        source_traceability=[*RAZOR_FILES, *ANGULARJS_FILES, *SHARED_UI_FILES, *STYLE_FILES, *ASSET_FILES],
    )
