"""Deterministic demo input. This is not customer or legacy-source design data."""

FIGMA_DASHBOARD_FIXTURE = {
    "name": "Operational Dashboard Fixture",
    "document": {
        "id": "0:0", "name": "Document", "type": "DOCUMENT", "children": [{
            "id": "1:0", "name": "Dashboard", "type": "CANVAS", "children": [{
                "id": "1:1", "name": "Operational Dashboard", "type": "FRAME",
                "layoutMode": "VERTICAL", "itemSpacing": 24,
                "paddingLeft": 32, "paddingRight": 32, "paddingTop": 24, "paddingBottom": 24,
                "absoluteBoundingBox": {"width": 1440, "height": 1024},
                "constraints": {"horizontal": "STRETCH", "vertical": "TOP"},
                "children": [
                    {"id": "1:2", "name": "Dashboard heading", "type": "TEXT", "characters": "Operational Dashboard", "style": {"fontFamily": "Source Sans 3", "fontWeight": 700, "fontSize": 32, "lineHeightPx": 40}, "fills": [{"type": "SOLID", "color": {"r": 0.06, "g": 0.17, "b": 0.2, "a": 1}}]},
                    {"id": "1:3", "name": "Reporting year selector", "type": "COMPONENT", "componentPropertyDefinitions": {"year": {"type": "TEXT"}}, "layoutMode": "HORIZONTAL", "itemSpacing": 8},
                    {"id": "1:4", "name": "Summary cards", "type": "FRAME", "layoutMode": "HORIZONTAL", "itemSpacing": 16, "children": [
                        {"id": "1:5", "name": "Expense summary card", "type": "INSTANCE", "componentId": "2:1"},
                        {"id": "1:6", "name": "Patient summary card", "type": "INSTANCE", "componentId": "2:1"},
                        {"id": "1:7", "name": "Clinic summary card", "type": "INSTANCE", "componentId": "2:1"}
                    ]}
                ]
            }]
        }],
    },
    "components": {"2:1": {"key": "fixture-summary-card", "name": "Summary card", "description": "Reusable summary region"}},
    "styles": {"heading": {"key": "fixture-heading", "name": "Heading / Page", "styleType": "TEXT"}},
    "fixtureRequirementLinks": [
        {"design_ref": "figma://file/FIXTURE_DASHBOARD?node-id=1%3A1", "requirement_ref": "FR-01", "relationship": "SUPPORTS", "description": "Dashboard frame supports the approved dashboard access presentation."},
        {"design_ref": "figma://file/FIXTURE_DASHBOARD?node-id=1%3A3", "requirement_ref": "FR-02", "relationship": "SUPPORTS", "description": "Explicit reporting-year selector supports yearly report presentation."}
    ]
}
