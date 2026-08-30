Before any further graph correction or visualization work, perform a read-only
HealthClinic application discovery.

Read:
PROJECT_MEMORY.md
PROGRESS.md
DECISIONS.md
config/profiles/healthclinic-dashboard.yaml
docs/validation/healthclinic-dashboard-neo4j-visual-demo.md

Create and save this prompt as:
docs/prompts/019-healthclinic-ui-technology-discovery.md

Goal:
Understand the real legacy HealthClinic application structure before deciding
the exact Angular 22 modernization scope.

Rules:

- Read only. Do not modify source/.
- Do not change graph code, Neo4j, Docker, profiles, or generated artifacts.
- Do not run LLM source analysis.
- Do not infer modern Angular from AngularJS.
- Distinguish ASP.NET MVC/Razor, AngularJS 1.x, modern Angular, Cordova/mobile,
  API/backend, and non-UI projects using actual file/package/source evidence.

Inspect source/HealthClinic.biz and produce:

docs/validation/healthclinic-ui-technology-discovery.md

The report must include:

1. Repository/application map:

   - solution files
   - web applications
   - mobile/Cordova applications
   - backend/API projects
   - shared libraries

2. UI technology inventory with actual evidence:

   - ASP.NET MVC/Razor files and main locations
   - AngularJS evidence such as angular.module(...)
   - modern Angular evidence only if package.json contains @angular/core,
     angular.json, or equivalent proof
   - Cordova evidence
   - React/Vue/other UI evidence, if present

3. For src/MyHealth.Web specifically:

   - server-rendered Razor UI entry points
   - MVC controllers
   - legacy AngularJS folders and their role
   - whether AngularJS is embedded in Razor pages or is a separate SPA area
   - API calls used by the Dashboard flow

4. Modernization recommendation:

   - a Razor-first Angular 22 migration scope
   - a hybrid Razor + AngularJS-to-Angular-22 migration scope
   - which scope is best for a two-to-three-day customer POC and why

5. Explicit terminology for the customer:

   - “Legacy ASP.NET MVC/Razor UI”
   - “Legacy AngularJS 1.x client-side code”, only where proven
   - “Target Angular 22 application”
   - never call AngularJS “Angular 22” or “modern Angular”

6. State whether the current healthclinic-dashboard profile is suitable as:

   - a complete legacy UI-flow demo, or
   - a pure .NET/Razor-to-Angular demo,
     and explain what profile changes would be needed.

Update only PROJECT_MEMORY.md and PROGRESS.md with the true discovery outcome.
Do not commit automatically.

Show me the report, the exact evidence found, Git status, and files ready to
commit.
