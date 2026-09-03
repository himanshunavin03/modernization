# Existing UI Reconstruction

- Feature: `feature-operational-dashboard-insights`
- Design source: `EXISTING_APPLICATION_UI`
- Figma fixture authority: `NONE`

## Existing UI To Angular

- **Private application header** -> `PrivateShellComponent` (UI-SH-01)
- **Collapsible navigation drawer** -> `PrivateShellComponent` (UI-SH-02)
- **Dashboard route outlet and loading overlay** -> `PrivateShellComponent` (UI-RZ-04)
- **Clinic summary card row** -> `DashboardFeatureComponent` (UI-NG1-06)
- **New patients summary** -> `SummaryCardComponent` (UI-NG1-06)
- **Month benefits summary** -> `SummaryCardComponent` (UI-NG1-06)
- **Annual benefits summary** -> `SummaryCardComponent` (UI-NG1-06)
- **Income and expenses yearly chart** -> `DashboardChartComponent` (UI-NG1-06)
- **Patient visits yearly chart** -> `DashboardChartComponent` (UI-NG1-06)
- **Private application footer** -> `PrivateShellComponent` (UI-RZ-05)

## Controls

- **Menu toggle** -> `PrivateShellComponent`
- **Dashboard navigation link** -> `PrivateShellComponent`
- **Previous income and expense year** -> `YearNavigatorComponent`
- **Next income and expense year** -> `YearNavigatorComponent`
- **Previous patient year** -> `YearNavigatorComponent`
- **Next patient year** -> `YearNavigatorComponent`

## Preserved Visual Identity

- `private-shell`: `#1d1e2a`
- `summary-patients`: `#00d8cc`
- `summary-month`: `#71717f`
- `summary-annual`: `#b8b8b9`
- `accent`: `#ff1770`
- `content-background`: `#f0f0f0`
- `body-font`: `Raleway`
- `numeric-font`: `Roboto`

## Clarifications

- **Header identity and broader navigation:** The current user's display name and non-Dashboard navigation authorization depend on APIs outside the approved hero contract; the generated hero shell does not fabricate them.
- **Legacy chart tooltip animation:** The generated accessible SVG presentation preserves series, months, colors, and hierarchy without copying obsolete Chart.js/jQuery tooltip mechanics; exact hover animation awaits visual review.
- **Legacy icon font glyphs:** Hero controls use accessible text symbols instead of copying the application-wide icon font; exact glyph equivalence awaits visual review.
