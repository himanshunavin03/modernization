# Complete Application Failure Disposition

The original 47 Windows access-violation failures (`3221225477`) were rerun through the isolated worker fallback. The disposition is evidence-based: generated/designer filenames, minified/tooling filenames, third-party path segments, or upstream license/library headers become opaque dependencies. All other files use the conservative first-party fallback and retain no invented AST or semantic facts.

| Disposition | Count | Exact source evidence |
| --- | ---: | --- |
| First-party conservative fallback | 3 | `src/MyHealth.Client.Desktop/ViewModels/NewAppointmentViewModel.cs`; `src/MyHealth.SugarTracker/SugarTrackerWeb/App/Home/Home.js`; `src/MyHealth.Web/Views/Home/Index.cshtml` |
| Generated/designer opaque dependency | 2 | `Components/AndHUD-1.3.1/samples/AndHUD.Sample/AndHUD.Sample/Resources/Resource.designer.cs`; `src/MyHealth.Client.Droid/Resources/Resource.Designer.cs` |
| Third-party opaque dependency | 43 | `src/MyHealth.Client.Cordova/content/js/MobileServices.Web.js`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Content/jquery-ui-1.11.4.custom/external/jquery/jquery.js`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Content/jquery-ui-1.11.4.custom/index.html`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Content/jquery-ui-1.11.4.custom/jquery-ui.js`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Scripts/jquery-1.9.1.intellisense.js`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Scripts/jquery-1.9.1.js`; and the 37 `src/MyHealth.SugarTracker/SugarTrackerWeb/Scripts/Office/1.1/` files listed in the canonical `OpaqueSource` node evidence. |
| Tooling/minified opaque dependency | 2 | `src/MyHealth.SugarTracker/SugarTrackerWeb/Scripts/Office/1.1/office-vsdoc.js`; `src/MyHealth.SugarTracker/SugarTrackerWeb/Scripts/Office/1.1/outlook-win32.debug-vsdoc.js` |

The exact per-file classification and rationale are carried in each generated `OpaqueSource.properties.classification` record in `artifacts/legacy-dashboard-complete-application-demo-v1/knowledge-graph.json`; no opaque record asserts syntax or semantic understanding.

Final rerun status: `complete_with_opaque_dependencies`, 2,384 files, 0 first-party extraction failures, 45 proven opaque dependencies, and 37 review warnings. No Neo4j load or viewer export has been performed by this correction.
