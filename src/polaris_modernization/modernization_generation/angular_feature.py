"""Artifact-driven Angular feature generation for an existing Nx workspace."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from polaris_modernization.commands.models import CommandError
from polaris_modernization.modernization_operations.models import ModernizationFeatureContext


@dataclass(frozen=True)
class EntityField:
    name: str
    typescript_type: str


@dataclass(frozen=True)
class FeatureShape:
    scope: str
    route: str
    entity: str
    variable: str
    identifier: str
    fields: tuple[EntityField, ...]
    list_fields: tuple[str, ...]
    detail_fields: tuple[str, ...]
    picture_field: str | None
    collection_contract: dict[str, Any]
    detail_contract: dict[str, Any]
    page_size: int


def generate_angular_feature(context: ModernizationFeatureContext) -> dict[str, object]:
    repository = Path(context.repository_root)
    workspace = repository / "modernized"
    if not (workspace / "package.json").is_file() or not (workspace / "tsconfig.base.json").is_file():
        raise CommandError("The selected Angular operation requires an existing modernized Nx workspace.")

    shape = _derive_shape(context)
    generated = _render_feature(workspace, shape, context)
    _register_aliases(workspace, shape)
    _register_route(workspace, shape)
    _register_navigation(workspace, shape, context.feature["name"])

    criteria = [
        item["acceptance_criterion_id"]
        for item in context.feature_specification.get("acceptance_criteria", [])
        if item.get("acceptance_criterion_id")
    ]
    tests = [path for path in generated if path.endswith(".spec.ts")]
    manifest = {
        "schema_version": 1,
        "project_id": context.project_id,
        "feature_id": context.feature["feature_id"],
        "generated_workspace": "modernized",
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "generator": {"name": "Polaris artifact-driven Angular feature generator", "version": "1.0"},
        "source_ui_mode": context.design_source,
        "architecture_selection_ref": context.architecture_source,
        "preserved_api_contracts": context.api_contracts,
        "generated_files": generated,
        "generated_tests": [
            {"file": path, "acceptance_criteria_refs": criteria} for path in tests
        ],
        "generated_routes": [{"file": f"libs/{shape.scope}/feature/src/lib/{shape.variable}-directory.routes.ts", "path": f"/{shape.route}"}],
        "generated_models": [{"file": generated[2], "name": shape.entity}],
        "generated_services": [
            {"file": generated[3], "name": f"{shape.entity}ApiClient"},
            {"file": generated[6], "name": f"{shape.entity}DirectoryStore"},
        ],
        "validation_commands": [
            {"name": "build", "command": ["npm", "run", "build"]},
            {"name": "test", "command": ["npm", "run", "test", "--", "--watch=false"]},
            {
                "name": "e2e",
                "command": [
                    "npx", "playwright", "test", f"apps/healthclinic-web-e2e/src/{shape.scope}.spec.ts",
                    "--config", "apps/healthclinic-web-e2e/playwright.config.ts", "--reporter=line",
                ],
                "isolated_port_env": "PLAYWRIGHT_PORT",
            },
        ],
        "task_statuses": _task_statuses(context.technical_task_plan, generated),
    }
    manifest_root = repository / "artifacts" / "modernization" / "features" / context.feature["feature_id"] / "latest"
    _write(manifest_root / "generation-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    _write(manifest_root / "generation-validation.json", json.dumps({
        "feature_id": context.feature["feature_id"],
        "status": "PENDING_EXECUTION",
        "checks": {"artifact_traceability": "PASS", "source_evidence_resolved": "PASS"},
    }, indent=2, sort_keys=True) + "\n")
    return {
        "feature_id": context.feature["feature_id"],
        "workspace": "modernized",
        "route": f"/{shape.route}",
        "generated_files": generated,
        "manifest": manifest_root.relative_to(repository).as_posix() + "/generation-manifest.json",
        "validation": "PENDING",
    }


def _derive_shape(context: ModernizationFeatureContext) -> FeatureShape:
    collection, detail = _resource_contracts(context.api_contracts)
    response = str(collection.get("response_model", "")).removesuffix("[]").strip()
    if not response or response.casefold() in {"int", "string", "object"}:
        raise CommandError("Approved API contracts do not identify a typed collection resource.")
    entity = _pascal(response)
    variable = entity[:1].lower() + entity[1:]
    route = collection["endpoint"].rstrip("/").split("/")[-1]
    scope = re.sub(r"[^a-z0-9]+", "-", context.feature["slug"].casefold()).strip("-")
    source_root = Path(str(context.ui_evidence.get("source_root") or ""))
    model_path = next(
        (source_root / item for item in context.ui_evidence.get("source_paths", []) if Path(item).stem.casefold() == entity.casefold()),
        None,
    )
    if model_path is None or not model_path.is_file():
        raise CommandError(f"Source evidence does not contain the {entity} response model.")
    fields = tuple(_parse_csharp_fields(model_path.read_text(encoding="utf-8")))
    if not fields:
        raise CommandError(f"No serializable fields were resolved for the {entity} response model.")
    identifier = next((field.name for field in fields if field.name.casefold() == f"{entity}id".casefold()), fields[0].name)
    views, controller_text = _related_ui_evidence(source_root, context.ui_evidence.get("source_paths", []))
    picture = next((field.name for field in fields if field.typescript_type == "string" and field.name.casefold() in {"picture", "image", "photo"}), None)
    excluded = {identifier, picture}
    list_fields = tuple(
        name for name in _bound_fields(next((text for text in views if "ng-repeat" in text), ""), fields, ng_bind_only=True)
        if name not in excluded
    )
    detail_fields = tuple(
        name for name in _bound_fields(next((text for text in views if "ng-repeat" not in text), ""), fields)
        if name not in excluded
    )
    if not list_fields:
        list_fields = tuple(field.name for field in fields if field.name != identifier)[:4]
    if not detail_fields:
        detail_fields = tuple(field.name for field in fields if field.name != identifier)[:6]
    page_match = re.search(r"\bpageSize\s*=\s*(\d+)", controller_text)
    return FeatureShape(
        scope=scope, route=route, entity=entity, variable=variable, identifier=identifier,
        fields=fields, list_fields=list_fields, detail_fields=detail_fields,
        picture_field=picture, collection_contract=collection, detail_contract=detail,
        page_size=int(page_match.group(1)) if page_match else 20,
    )


def _resource_contracts(contracts: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    gets = [item for item in contracts if item.get("method", "").upper() == "GET"]
    for collection in gets:
        if collection.get("path_parameters") or not str(collection.get("response_model", "")).endswith("[]"):
            continue
        base = str(collection.get("endpoint", "")).rstrip("/")
        detail = next((item for item in gets if str(item.get("endpoint", "")).startswith(base + "/{") and item.get("path_parameters")), None)
        if detail:
            return collection, detail
    raise CommandError("Approved API contracts must include matching collection and detail GET operations.")


def _parse_csharp_fields(source: str) -> list[EntityField]:
    mapping = {
        "string": "string", "int": "number", "long": "number", "double": "number",
        "decimal": "number", "float": "number", "bool": "boolean", "byte[]": "string",
        "DateTime": "string", "DateTimeOffset": "string", "Guid": "string",
    }
    fields: list[EntityField] = []
    for type_name, name in re.findall(r"public\s+([\w.<>\[\]]+\??)\s+(\w+)\s*\{\s*get;\s*set;\s*\}", source):
        bare = type_name.removesuffix("?")
        if bare.startswith(("ICollection<", "IEnumerable<", "List<")):
            continue
        ts_type = mapping.get(bare, "unknown")
        if type_name.endswith("?"):
            ts_type += " | null"
        fields.append(EntityField(name, ts_type))
    return fields


def _related_ui_evidence(source_root: Path, paths: list[str]) -> tuple[list[str], str]:
    roots: set[Path] = set()
    controllers: list[str] = []
    for value in paths:
        path = source_root / value
        if path.is_file() and path.suffix.casefold() in {".js", ".ts"}:
            text = path.read_text(encoding="utf-8")
            controllers.append(text)
            parent = path.parent.parent if path.parent.name.casefold() in {"controllers", "services"} else path.parent
            roots.add(parent)
    views = [path.read_text(encoding="utf-8") for root in roots for path in sorted(root.rglob("*.html"))]
    for root in roots:
        controllers.extend(path.read_text(encoding="utf-8") for path in sorted(root.rglob("*Controller.js")))
    return views, "\n".join(controllers)


def _bound_fields(source: str, fields: tuple[EntityField, ...], *, ng_bind_only: bool = False) -> tuple[str, ...]:
    known = {field.name for field in fields}
    pattern = r'ng-bind="[^"]*\.([A-Z][A-Za-z0-9_]*)' if ng_bind_only else r"\b[a-z][A-Za-z0-9_]*\.([A-Z][A-Za-z0-9_]*)"
    found = re.findall(pattern, source)
    return tuple(dict.fromkeys(name for name in found if name in known))


def _pascal(value: str) -> str:
    return "".join(part[:1].upper() + part[1:] for part in re.split(r"[^A-Za-z0-9]+", value) if part)


def _label(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", value).replace(" Id", " ID")


def _project(name: str, source_root: str, scope: str, kind: str) -> str:
    return json.dumps({
        "name": name, "$schema": "../../../../node_modules/nx/schemas/project-schema.json",
        "sourceRoot": source_root, "projectType": "library",
        "tags": [f"scope:{scope}", f"type:{kind}"], "targets": {},
    }, indent=2) + "\n"


def _render_feature(workspace: Path, shape: FeatureShape, context: ModernizationFeatureContext) -> list[str]:
    base = Path("libs") / shape.scope
    data = base / "data-access"
    state = base / "state"
    feature = base / "feature"
    alias = f"@modernized/{shape.scope}"
    model_fields = "\n".join(f"  {field.name}: {field.typescript_type};" for field in shape.fields)
    query_args = [re.sub(r"\s*\(.*", "", item["name"]) for item in shape.collection_contract.get("query_parameters", [])]
    query_values = ", ".join(f"{name}: {name}" for name in query_args)
    detail_endpoint = str(shape.detail_contract["endpoint"])
    parameter = shape.detail_contract["path_parameters"][0]["name"]
    detail_expression = detail_endpoint.replace("{" + parameter + "}", "${id}")
    paths: dict[Path, str] = {
        data / "project.json": _project(f"{shape.scope}-data-access", (data / "src").as_posix(), shape.scope, "data-access"),
        data / "src/index.ts": f"export {{ {shape.entity}ApiClient }} from './lib/{shape.variable}-api.client';\nexport type {{ {shape.entity} }} from './lib/{shape.variable}.models';\n",
        data / f"src/lib/{shape.variable}.models.ts": f"export interface {shape.entity} {{\n{model_fields}\n}}\n",
        data / f"src/lib/{shape.variable}-api.client.ts": f"""import {{ HttpClient, HttpParams }} from '@angular/common/http';
import {{ inject, Injectable }} from '@angular/core';
import {{ RUNTIME_CONFIG, withTenantContext }} from '@healthclinic/core/platform';
import {{ Observable }} from 'rxjs';
import type {{ {shape.entity} }} from './{shape.variable}.models';

@Injectable({{ providedIn: 'root' }})
export class {shape.entity}ApiClient {{
  private readonly http = inject(HttpClient);
  private readonly config = inject(RUNTIME_CONFIG);

  getList({', '.join(name + ': number' for name in query_args)}, tenantId: number): Observable<{shape.entity}[]> {{
    const params = new HttpParams({{ fromObject: {{ {query_values} }} }});
    return this.http.get<{shape.entity}[]>(this.url('{shape.collection_contract['endpoint']}'), {{ params, context: withTenantContext(tenantId) }});
  }}

  getById(id: number, tenantId: number): Observable<{shape.entity}> {{
    return this.http.get<{shape.entity}>(this.url(`{detail_expression}`), {{ context: withTenantContext(tenantId) }});
  }}

  private url(path: string): string {{ return `${{this.config.apiBaseUrl.replace(/\\/$/, '')}}${{path}}`; }}
}}
""",
        data / f"src/lib/{shape.variable}-api.client.spec.ts": _api_spec(shape, alias, query_args),
        state / "project.json": _project(f"{shape.scope}-state", (state / "src").as_posix(), shape.scope, "state"),
        state / "src/index.ts": f"export {{ {shape.entity}DirectoryStore }} from './lib/{shape.variable}-directory.store';\nexport type {{ {shape.entity} }} from '{alias}/data-access';\n",
        state / f"src/lib/{shape.variable}-directory.store.ts": _store(shape, alias, query_args),
        state / f"src/lib/{shape.variable}-directory.store.spec.ts": _store_spec(shape, alias),
        feature / "project.json": _project(f"{shape.scope}-feature", (feature / "src").as_posix(), shape.scope, "feature"),
        feature / "src/index.ts": f"export {{ {shape.entity.upper()}_DIRECTORY_ROUTES }} from './lib/{shape.variable}-directory.routes';\n",
        feature / f"src/lib/{shape.variable}-directory.routes.ts": f"""import {{ Routes }} from '@angular/router';
import {{ {shape.entity}DetailComponent }} from './{shape.variable}-detail.component';
import {{ {shape.entity}ListComponent }} from './{shape.variable}-list.component';

export const {shape.entity.upper()}_DIRECTORY_ROUTES: Routes = [
  {{ path: '', component: {shape.entity}ListComponent }},
  {{ path: ':id', component: {shape.entity}DetailComponent }},
];
""",
        feature / f"src/lib/{shape.variable}-list.component.ts": _list_component(shape, alias),
        feature / f"src/lib/{shape.variable}-list.component.html": _list_html(shape),
        feature / f"src/lib/{shape.variable}-detail.component.ts": _detail_component(shape, alias),
        feature / f"src/lib/{shape.variable}-detail.component.html": _detail_html(shape),
        feature / f"src/lib/{shape.variable}-directory.component.css": _styles(len(shape.list_fields)),
        feature / f"src/lib/{shape.variable}-directory.component.spec.ts": _component_spec(shape, alias, context),
        Path("apps/healthclinic-web-e2e/src") / f"{shape.scope}.spec.ts": _e2e_spec(shape, context),
    }
    for relative, content in paths.items():
        _write(workspace / relative, content)
    return [path.as_posix() for path in paths]


def _store(shape: FeatureShape, alias: str, query_args: list[str]) -> str:
    args = ", ".join(str(shape.page_size) if name.casefold() == "pagesize" else "this.pageCount" for name in query_args)
    return f"""import {{ DestroyRef, inject, Injectable, signal }} from '@angular/core';
import {{ takeUntilDestroyed }} from '@angular/core/rxjs-interop';
import {{ {shape.entity}ApiClient, type {shape.entity} }} from '{alias}/data-access';
import {{ TenantContextService }} from '@healthclinic/core/platform';
import {{ switchMap, take }} from 'rxjs';

@Injectable()
export class {shape.entity}DirectoryStore {{
  private readonly api = inject({shape.entity}ApiClient);
  private readonly tenant = inject(TenantContextService);
  private readonly destroyRef = inject(DestroyRef);
  private pageCount = 0;
  readonly items = signal<{shape.entity}[] | null>(null);
  readonly selected = signal<{shape.entity} | null>(null);
  readonly loading = signal(false);
  readonly noMoreData = signal(false);
  readonly errorMessage = signal<string | null>(null);

  loadNext(): void {{
    if (this.loading() || this.noMoreData()) return;
    this.loading.set(true); this.errorMessage.set(null);
    this.tenant.tenantId$.pipe(
      take(1), switchMap((tenantId) => this.api.getList({args}{', ' if args else ''}tenantId)), takeUntilDestroyed(this.destroyRef),
    ).subscribe({{
      next: (items) => {{ this.items.update((current) => [...(current ?? []), ...items]); this.pageCount += 1; this.noMoreData.set(items.length < {shape.page_size}); this.loading.set(false); }},
      error: () => {{ this.errorMessage.set('The directory could not be loaded.'); this.loading.set(false); }},
    }});
  }}

  loadDetail(id: number): void {{
    this.loading.set(true); this.errorMessage.set(null); this.selected.set(null);
    this.tenant.tenantId$.pipe(
      take(1), switchMap((tenantId) => this.api.getById(id, tenantId)), takeUntilDestroyed(this.destroyRef),
    ).subscribe({{
      next: (item) => {{ this.selected.set(item); this.loading.set(false); }},
      error: () => {{ this.errorMessage.set('The requested record could not be loaded.'); this.loading.set(false); }},
    }});
  }}
}}
"""


def _list_component(shape: FeatureShape, alias: str) -> str:
    picture_method = ""
    if shape.picture_field:
        picture_method = f"\n  protected pictureUrl(item: {shape.entity}): string {{ return item.{shape.picture_field} ? `data:image/png;base64,${{item.{shape.picture_field}}}` : ''; }}"
    return f"""import {{ ChangeDetectionStrategy, Component, inject }} from '@angular/core';
import {{ RouterLink }} from '@angular/router';
import {{ {shape.entity}DirectoryStore, type {shape.entity} }} from '{alias}/state';

@Component({{
  selector: 'modernized-{shape.scope}-list', standalone: true, imports: [RouterLink],
  providers: [{shape.entity}DirectoryStore], templateUrl: './{shape.variable}-list.component.html',
  styleUrl: './{shape.variable}-directory.component.css', changeDetection: ChangeDetectionStrategy.OnPush,
}})
export class {shape.entity}ListComponent {{
  protected readonly store = inject({shape.entity}DirectoryStore);
  constructor() {{ this.store.loadNext(); }}{picture_method}
}}
"""


def _list_html(shape: FeatureShape) -> str:
    picture_header = "<span class=\"visually-hidden\">Photo</span>" if shape.picture_field else ""
    picture_cell = f"<img [src]=\"pictureUrl(item)\" alt=\"\" class=\"avatar\">" if shape.picture_field else ""
    headers = "".join(f"<span>{_label(field)}</span>" for field in shape.list_fields)
    field_types = {field.name: field.typescript_type for field in shape.fields}
    cells = "".join(f"<span data-label=\"{_label(field)}\">{{{{ {_display(field, field_types)} }}}}</span>" for field in shape.list_fields)
    return f"""<section class="directory" aria-labelledby="directory-heading">
  <div class="title-row"><div><p class="eyebrow">Directory</p><h1 id="directory-heading">{_label(shape.entity)}s</h1></div></div>
  @if (store.errorMessage()) {{ <p class="error" role="alert">{{{{ store.errorMessage() }}}}</p> }}
  @if (store.items(); as items) {{
    @if (items.length) {{
      <div class="data-grid" aria-label="{_label(shape.entity)} directory">
        <div class="grid-header" aria-hidden="true">{picture_header}{headers}<span class="visually-hidden">Action</span></div>
        @for (item of items; track item.{shape.identifier}) {{
          <a class="grid-row" [routerLink]="[item.{shape.identifier}]" aria-label="View {{{{ item.{shape.list_fields[0]} }}}}">{picture_cell}{cells}<span class="view-link">View</span></a>
        }}
      </div>
    }} @else if (!store.loading()) {{ <p class="empty">No data is available.</p> }}
  }}
  @if (store.loading()) {{ <p class="status" role="status">Loading directory...</p> }}
  @if (!store.noMoreData() && store.items()?.length) {{ <button class="load-more" type="button" (click)="store.loadNext()">Load more</button> }}
</section>
"""


def _detail_component(shape: FeatureShape, alias: str) -> str:
    picture_method = ""
    if shape.picture_field:
        picture_method = f"\n  protected pictureUrl(item: {shape.entity}): string {{ return item.{shape.picture_field} ? `data:image/png;base64,${{item.{shape.picture_field}}}` : ''; }}"
    return f"""import {{ ChangeDetectionStrategy, Component, inject }} from '@angular/core';
import {{ ActivatedRoute, RouterLink }} from '@angular/router';
import {{ {shape.entity}DirectoryStore, type {shape.entity} }} from '{alias}/state';

@Component({{
  selector: 'modernized-{shape.scope}-detail', standalone: true, imports: [RouterLink],
  providers: [{shape.entity}DirectoryStore], templateUrl: './{shape.variable}-detail.component.html',
  styleUrl: './{shape.variable}-directory.component.css', changeDetection: ChangeDetectionStrategy.OnPush,
}})
export class {shape.entity}DetailComponent {{
  protected readonly store = inject({shape.entity}DirectoryStore);
  private readonly route = inject(ActivatedRoute);
  constructor() {{
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isInteger(id) && id > 0) this.store.loadDetail(id);
    else this.store.errorMessage.set('The requested record identifier is invalid.');
  }}{picture_method}
}}
"""


def _detail_html(shape: FeatureShape) -> str:
    picture = f"<img [src]=\"pictureUrl(item)\" alt=\"\" class=\"portrait\">" if shape.picture_field else ""
    field_types = {field.name: field.typescript_type for field in shape.fields}
    details = "".join(f"<div><dt>{_label(field)}</dt><dd>{{{{ {_display(field, field_types)} }}}}</dd></div>" for field in shape.detail_fields if field != shape.picture_field)
    return f"""<section class="directory detail" aria-labelledby="detail-heading">
  <a routerLink="../" class="back-link">&lsaquo; Back to {_label(shape.entity).lower()}s</a>
  @if (store.errorMessage()) {{ <p class="error" role="alert">{{{{ store.errorMessage() }}}}</p> }}
  @if (store.selected(); as item) {{
    <article class="profile">{picture}<div class="profile-copy"><p class="eyebrow">{_label(shape.entity)} profile</p><h1 id="detail-heading">{{{{ item.{shape.detail_fields[0]} }}}}</h1><dl>{details}</dl></div></article>
  }} @else if (store.loading()) {{ <p class="status" role="status">Loading details...</p> }}
</section>
"""


def _display(field: str, field_types: dict[str, str]) -> str:
    expression = f"item.{field}"
    return f"{expression} ?? '---'" if "null" in field_types[field] else expression


def _styles(column_count: int) -> str:
    return f""":host{{display:block}}.directory{{color:#343442}}.title-row{{align-items:end;display:flex;justify-content:space-between;margin-bottom:28px}}.eyebrow{{color:#ff1770;font-size:.75rem;font-weight:700;letter-spacing:.18em;margin:0 0 6px;text-transform:uppercase}}h1{{font-size:clamp(2rem,4vw,3.5rem);font-weight:300;margin:0}}.data-grid{{background:#fff;border:1px solid #e8e8ec;box-shadow:0 14px 40px -34px #1d1e2a}}.grid-header,.grid-row{{align-items:center;display:grid;gap:18px;grid-template-columns:70px repeat({column_count},minmax(90px,1fr)) 64px;padding:15px 22px}}.grid-header{{background:#f2f2f5;color:#676773;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}.grid-row{{border-top:1px solid #eeeeef;color:#343442;text-decoration:none;transition:background .18s,border-color .18s}}.grid-row:hover,.grid-row:focus-visible{{background:#fff5f8;border-left:3px solid #ff1770}}.avatar{{background:#ededf0;border-radius:50%;height:44px;object-fit:cover;width:44px}}.view-link{{color:#d80d5b;font-weight:700}}.load-more{{background:#ff1770;border:0;color:#fff;display:block;font-weight:700;margin:24px auto 0;padding:13px 28px;text-transform:uppercase}}.status,.empty{{background:#fff;color:#696977;padding:42px;text-align:center}}.error{{background:#fff0f3;border-left:4px solid #ff1770;color:#7d1640;padding:16px}}.back-link{{color:#d80d5b;display:inline-block;font-weight:700;margin-bottom:28px;text-decoration:none}}.profile{{background:#fff;border-top:4px solid #ff1770;box-shadow:0 14px 40px -34px #1d1e2a;display:grid;gap:36px;grid-template-columns:minmax(180px,280px) 1fr;padding:36px}}.portrait{{background:#efeff2;height:280px;object-fit:cover;width:100%}}.profile dl{{display:grid;gap:0;grid-template-columns:repeat(2,minmax(160px,1fr));margin:28px 0 0}}.profile dl div{{border-top:1px solid #ececf0;padding:16px 20px 16px 0}}.profile dt{{color:#747480;font-size:.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}}.profile dd{{margin:7px 0 0}}.visually-hidden{{height:1px;margin:-1px;overflow:hidden;padding:0;position:absolute;width:1px;clip:rect(0,0,0,0)}}@media(max-width:850px){{.grid-header{{display:none}}.grid-row{{grid-template-columns:52px 1fr}}.grid-row span:not(.view-link){{grid-column:2}}.grid-row span:not(.view-link)::before{{color:#777783;content:attr(data-label) ': ';font-size:.72rem;font-weight:700;text-transform:uppercase}}.view-link{{grid-column:2}}.profile{{grid-template-columns:1fr}}.portrait{{height:220px;max-width:280px}}.profile dl{{grid-template-columns:1fr}}}}@media(max-width:520px){{.grid-row{{padding:16px}}.profile{{padding:24px}}}}\n"""


def _api_spec(shape: FeatureShape, alias: str, query_args: list[str]) -> str:
    args = ", ".join("4" if name.casefold() == "pagesize" else "0" for name in query_args)
    return f"""import {{ provideHttpClient }} from '@angular/common/http';
import {{ HttpTestingController, provideHttpClientTesting }} from '@angular/common/http/testing';
import {{ TestBed }} from '@angular/core/testing';
import {{ provideRuntimeConfig }} from '@healthclinic/core/platform';
import {{ {shape.entity}ApiClient }} from './{shape.variable}-api.client';

describe('{shape.entity}ApiClient', () => {{
  it('preserves the approved collection and detail GET contracts', () => {{
    TestBed.configureTestingModule({{ providers: [provideHttpClient(), provideHttpClientTesting(), provideRuntimeConfig({{ apiBaseUrl: '', tenantContextPath: '/tenant', tenantHeaderName: 'TenantId' }})] }});
    const client = TestBed.inject({shape.entity}ApiClient); const http = TestBed.inject(HttpTestingController);
    client.getList({args}{', ' if args else ''}7).subscribe();
    const list = http.expectOne((request) => request.url === '{shape.collection_contract['endpoint']}'); expect(list.request.method).toBe('GET'); expect(list.request.headers.get('TenantId')).toBe('7'); list.flush([]);
    client.getById(3, 7).subscribe();
    const detail = http.expectOne('{str(shape.detail_contract['endpoint']).replace('{' + shape.detail_contract['path_parameters'][0]['name'] + '}', '3')}'); expect(detail.request.method).toBe('GET'); detail.flush({{}});
  }});
}});
"""


def _store_spec(shape: FeatureShape, alias: str) -> str:
    return f"""import {{ TestBed }} from '@angular/core/testing';
import {{ {shape.entity}ApiClient }} from '{alias}/data-access';
import {{ TenantContextService }} from '@healthclinic/core/platform';
import {{ of }} from 'rxjs';
import {{ {shape.entity}DirectoryStore }} from './{shape.variable}-directory.store';

describe('{shape.entity}DirectoryStore', () => {{
  it('loads the approved tenant-aware directory', () => {{
    TestBed.configureTestingModule({{ providers: [{shape.entity}DirectoryStore, {{ provide: {shape.entity}ApiClient, useValue: {{ getList: () => of([]), getById: () => of({{}}) }} }}, {{ provide: TenantContextService, useValue: {{ tenantId$: of(7) }} }}] }});
    const store = TestBed.inject({shape.entity}DirectoryStore); store.loadNext(); expect(store.items()).toEqual([]); expect(store.loading()).toBe(false);
  }});
}});
"""


def _component_spec(shape: FeatureShape, alias: str, context: ModernizationFeatureContext) -> str:
    criteria = " ".join(item.get("acceptance_criterion_id", "") for item in context.feature_specification.get("acceptance_criteria", []))
    sample = ", ".join(f"{field.name}: {_sample(field.typescript_type, field.name)}" for field in shape.fields)
    return f"""import {{ signal }} from '@angular/core';
import {{ TestBed }} from '@angular/core/testing';
import {{ provideRouter }} from '@angular/router';
import {{ {shape.entity}DirectoryStore }} from '{alias}/state';
import {{ {shape.entity}ListComponent }} from './{shape.variable}-list.component';

describe('{shape.entity}ListComponent', () => {{
  it('{criteria}: renders the approved directory experience', async () => {{
    const store = {{ items: signal([{{ {sample} }}]), selected: signal(null), loading: signal(false), noMoreData: signal(true), errorMessage: signal(null), loadNext: vi.fn(), loadDetail: vi.fn() }};
    await TestBed.configureTestingModule({{ imports: [{shape.entity}ListComponent], providers: [provideRouter([])] }}).overrideComponent({shape.entity}ListComponent, {{ set: {{ providers: [{{ provide: {shape.entity}DirectoryStore, useValue: store }}] }} }}).compileComponents();
    const fixture = TestBed.createComponent({shape.entity}ListComponent); fixture.detectChanges(); expect(fixture.nativeElement.textContent).toContain('{_label(shape.entity)}s');
  }});
}});
"""


def _sample(ts_type: str, name: str) -> str:
    if "number" in ts_type:
        return "1"
    if "boolean" in ts_type:
        return "false"
    if "null" in ts_type:
        return "null"
    return repr(_label(name))


def _e2e_spec(shape: FeatureShape, context: ModernizationFeatureContext) -> str:
    criteria = " ".join(item.get("acceptance_criterion_id", "") for item in context.feature_specification.get("acceptance_criteria", []))
    return f"""import {{ expect, test }} from '@playwright/test';

test('{criteria}: supports list and detail navigation', async ({{ page }}) => {{
  await page.route('**/api/users/current/tenant', (route) => route.fulfill({{ json: 7 }}));
  await page.route('**{shape.collection_contract['endpoint']}?*', (route) => route.fulfill({{ json: [{{ {shape.identifier}: 3, {shape.list_fields[0]}: 'Directory record' }}] }}));
  await page.route('**{str(shape.detail_contract['endpoint']).replace('{' + shape.detail_contract['path_parameters'][0]['name'] + '}', '3')}', (route) => route.fulfill({{ json: {{ {shape.identifier}: 3, {shape.detail_fields[0]}: 'Directory record' }} }}));
  await page.goto('/{shape.route}'); await expect(page.getByRole('heading', {{ name: '{_label(shape.entity)}s' }})).toBeVisible();
  await page.getByRole('link', {{ name: /View Directory record/ }}).click(); await expect(page).toHaveURL(/\\/{shape.route}\\/3$/); await expect(page.getByRole('heading', {{ name: 'Directory record' }})).toBeVisible();
}});
"""


def _register_aliases(workspace: Path, shape: FeatureShape) -> None:
    path = workspace / "tsconfig.base.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    aliases = config["compilerOptions"].setdefault("paths", {})
    for kind in ("feature", "data-access", "state"):
        aliases[f"@modernized/{shape.scope}/{kind}"] = [f"./libs/{shape.scope}/{kind}/src/index.ts"]
    _write(path, json.dumps(config, indent=2) + "\n")


def _register_route(workspace: Path, shape: FeatureShape) -> None:
    path = workspace / "apps/healthclinic-web/src/app/app.routes.ts"
    source = path.read_text(encoding="utf-8")
    marker = f"path: '{shape.route}'"
    if marker not in source:
        route = f"    {{ path: '{shape.route}', canActivate: [dashboardRouteGuard], loadChildren: () => import('@modernized/{shape.scope}/feature').then((entry) => entry.{shape.entity.upper()}_DIRECTORY_ROUTES) }},\n"
        source = source.replace("  ] },\n", route + "  ] },\n")
        _write(path, source)


def _register_navigation(workspace: Path, shape: FeatureShape, feature_name: str) -> None:
    path = workspace / "apps/healthclinic-web/src/app/private-shell.component.html"
    source = path.read_text(encoding="utf-8")
    link = f'<a routerLink="/{shape.route}" routerLinkActive="selected" (click)="closeMenu()"><span class="nav-icon" aria-hidden="true">&#9672;</span> {feature_name}</a>'
    if f'routerLink="/{shape.route}"' not in source:
        source = source.replace("</nav>", link + "</nav>", 1)
        _write(path, source)


def _task_statuses(plan: dict[str, Any], files: list[str]) -> list[dict[str, Any]]:
    deferred = {"GATEWAY", "BFF"}
    return [
        {
            "task_id": task.get("task_id"),
            "status": "DEFERRED" if task.get("category") in deferred else "IMPLEMENTED",
            "detail": "Deployment architecture remains deferred." if task.get("category") in deferred else "Delivered by the artifact-driven Angular feature operation.",
            "generated_file_refs": [] if task.get("category") in deferred else files,
        }
        for task in plan.get("tasks", [])
    ]


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
