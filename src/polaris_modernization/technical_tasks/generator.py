"""Deterministic task composition from approved requirements and locked architecture."""
from __future__ import annotations

from langchain_core.runnables import RunnableLambda

from .models import TechnicalTaskModel


def _design_refs(design: dict) -> list[str]:
    refs = []
    for group in ("screens", "components", "component_instances", "controls"):
        refs.extend(item["design_ref"] for item in design.get(group, []) if item.get("design_ref"))
    return list(dict.fromkeys(refs))


def _compose(context: dict) -> list[dict]:
    feature = context["feature"]
    feature_id = feature["feature_id"]
    feature_name = feature["feature_name"]
    design = context["design"]
    design_refs = _design_refs(design)
    no_design_note = [] if design["status"] == "AVAILABLE" else [
        "Use existing application UI evidence and accessible implementation defaults because customer design input is unavailable."
    ]
    fr_refs = [item["id"] for item in context["requirements"]]
    story_refs = [item["story_id"] for item in context["stories"]]
    ac_refs = [item["authoritative_ac_ref"] for item in context["acceptance_criteria"]]
    api_refs = [item["api_id"] for item in context["api_contracts"]]

    selection = context["architecture"]
    selected_ids = set(selection["selected_decision_ids"])
    selected = [item for item in selection["decisions"] if item["id"] in selected_ids]

    def architecture_refs(*categories: str) -> list[str]:
        refs = [item["id"] for item in selected if item["category"] in categories]
        return refs or [item["id"] for item in selected[:1]]

    templates = [
        ("SCAFFOLD", f"Establish the delivery workspace for {feature_name}", "Create the selected frontend workspace foundation.", ("Frontend Platform", "Workspace", "Change Detection", "Delivery"), [], False, False, ["Configure the selected frontend platform and strict compiler settings.", "Apply workspace boundary, build, and quality policies."], ["Workspace build and quality commands pass."], ["Feature workspace foundation"]),
        ("CONFIGURATION", f"Define the {feature_name} domain boundary", "Create enforceable ownership and dependency boundaries.", ("Workspace", "Application Topology"), ["TT-001"], False, False, ["Create feature, data-access, and reusable UI boundaries.", "Prevent presentation code from bypassing integration boundaries."], ["Dependency validation passes."], ["Feature and data-access boundaries"]),
        ("DESIGN_SYSTEM", f"Prepare accessible presentation primitives for {feature_name}", "Provide reusable presentation foundations without inventing behavior.", ("Design System", "Accessibility", "Workspace"), ["TT-001"], False, False, [*no_design_note, "Apply normalized design evidence only when available."], ["Presentation primitives meet keyboard, contrast, and responsive expectations."], ["Accessible presentation primitives"]),
        ("API", f"Model approved {feature_name} API contracts", "Create typed client models while preserving backend semantics.", ("API Client", "Workspace"), ["TT-002"], True, True, ["Represent every approved method, route, parameter, and response contract exactly.", "Keep transport logic outside presentation components."], ["Contract tests cover every approved API without inventing endpoints."], ["Typed API models and contract tests"]),
        ("GATEWAY", f"Plan gateway policies for {feature_name}", "Apply the selected ingress architecture without changing business APIs.", ("API Gateway", "Security", "Observability"), ["TT-004"], True, True, ["Preserve approved backend contracts through gateway routing.", "Define authentication, correlation, and observability policy responsibilities."], ["Route review proves existing contracts remain unchanged."], ["Gateway routing and policy plan"]),
        ("BFF", f"Design the future {feature_name} BFF boundary", "Plan frontend-specific orchestration without inventing business behavior.", ("Backend for Frontend", "Security", "Observability"), ["TT-005"], True, True, ["Label every future facade TARGET_CONTRACT_TO_BE_DESIGNED.", "Trace justified orchestration to approved APIs and requirements."], ["No future facade is represented as an existing API."], ["BFF responsibility design"]),
        ("INTEGRATION", f"Define the {feature_name} integration boundary", "Connect the Feature to selected target integration layers.", ("API Client", "Backend for Frontend"), ["TT-004", "TT-006"], True, True, ["Create typed integration ports for approved contracts.", "Keep future facade contracts explicitly unapproved until designed."], ["Feature code depends on typed integration ports."], ["Typed integration ports"]),
        ("ROUTING", f"Configure lazy routes for {feature_name}", "Expose approved Feature surfaces through selected routing patterns.", ("Routing", "Performance"), ["TT-002"], True, False, ["Register lazy Feature routes and selected guard boundaries.", "Do not invent identity-provider behavior."], ["Routes load lazily and preserve approved access behavior."], ["Feature route configuration"]),
        ("UI", f"Implement the {feature_name} feature shell", "Create the Feature container and approved presentation regions.", ("Frontend Platform", "Application Topology", "Design System"), ["TT-003", "TT-008"], True, False, [*no_design_note, "Render only behavior and information established by approved requirements."], ["The shell exposes all approved Feature workflows."], ["Standalone Feature shell"]),
        ("STATE", f"Implement {feature_name} state and asynchronous flow", "Separate synchronous UI state from asynchronous integration work.", ("Reactivity", "State Management", "Change Detection"), ["TT-004", "TT-007", "TT-009"], True, True, ["Use selected state primitives for local and derived UI state.", "Use selected asynchronous composition for API work and cancellation."], ["State and asynchronous behavior are independently testable."], ["Feature state and data orchestration"]),
        ("SECURITY_CONTEXT", f"Apply security and tenant context to {feature_name}", "Preserve approved access context through target integration boundaries.", ("Security", "Routing", "API Client"), ["TT-005", "TT-006", "TT-010"], True, True, ["Propagate approved security, tenant, and correlation context.", "Keep unresolved identity-provider choices explicit."], ["Tests prove context propagation without unsupported assumptions."], ["Security context integration"]),
        ("UI", f"Implement approved {feature_name} interactions", "Connect approved workflows to Feature state and integrations.", ("Frontend Platform", "Application Topology", "Design System"), ["TT-010", "TT-011"], True, True, ["Implement approved interactions and observable outcomes.", "Do not invent fields, validation rules, or business behavior."], ["Every interaction traces to approved requirements and contracts."], ["Feature interaction components"]),
        ("ACCESSIBILITY", f"Validate accessible {feature_name} behavior", "Apply selected accessibility and responsive standards.", ("Accessibility", "Design System"), ["TT-012"], True, False, ["Verify semantics, keyboard operation, focus, labels, contrast, and responsive reflow."], ["Automated and manual accessibility evidence is recorded."], ["Accessibility validation report"]),
        ("OBSERVABILITY", f"Add correlated telemetry for {feature_name}", "Make integration failures diagnosable without selecting a vendor.", ("Observability", "API Gateway", "Backend for Frontend"), ["TT-007", "TT-010", "TT-011"], True, True, ["Propagate correlation context across selected integration layers.", "Avoid recording sensitive business or tenant data."], ["Telemetry and failure handling are covered by tests."], ["Correlation and telemetry hooks"]),
        ("TEST", f"Implement unit and component coverage for {feature_name}", "Verify Feature state, UI, routing, contracts, and accessibility.", ("Testing", "Delivery"), ["TT-012", "TT-013", "TT-014"], True, True, ["Cover approved synchronous, asynchronous, presentation, routing, and contract behavior."], ["Affected unit and component suites pass."], ["Unit and component tests"]),
        ("TEST", f"Automate approved {feature_name} flows with Playwright", "Provide end-to-end evidence for approved acceptance criteria.", ("Testing", "Delivery"), ["TT-015"], True, True, ["Map each browser scenario to authoritative acceptance criteria.", "Use controlled data without redefining unresolved behavior."], ["Every approved criterion has executable traceability."], ["Playwright acceptance suite"]),
    ]

    decisions = {item["id"]: item for item in selected}
    tasks = []
    for order, template in enumerate(templates, 1):
        category, title, objective, architecture_categories, dependencies, feature_trace, api_trace, requirements, validation, deliverables = template
        arch_refs = architecture_refs(*architecture_categories)
        adr_refs = list(dict.fromkeys(decisions[ref]["adr_ref"] for ref in arch_refs if decisions[ref].get("adr_ref")))
        task_frs = fr_refs if feature_trace else []
        task_stories = story_refs if feature_trace else []
        task_ac = ac_refs if feature_trace else []
        task_apis = api_refs if api_trace else []
        task_design = design_refs if category in {"DESIGN_SYSTEM", "UI", "ACCESSIBILITY"} else []
        traceability = [
            f"Feature:{feature_id}",
            *[f"FR:{item}" for item in task_frs],
            *[f"Story:{item}" for item in task_stories],
            *[f"AC:{item}" for item in task_ac],
            *[f"Architecture:{item}" for item in arch_refs],
            *[f"ADR:{item}" for item in adr_refs],
            *[f"API:{item}" for item in task_apis],
            *[f"Design:{item}" for item in task_design],
        ]
        tasks.append(TechnicalTaskModel(
            task_id=f"TT-{order:03d}", feature_id=feature_id, title=title, objective=objective,
            category=category, description=f"{objective} This task consumes the locked architecture and makes no new architecture decision.",
            implementation_requirements=requirements, architecture_decision_refs=arch_refs, adr_refs=adr_refs,
            functional_requirement_refs=task_frs, story_refs=task_stories,
            acceptance_criteria_refs=task_ac, api_refs=task_apis, design_refs=task_design,
            dependencies=dependencies, validation_requirements=validation, deliverables=deliverables,
            implementation_order=order, blocking=False, open_questions=[], traceability=traceability,
        ).model_dump(mode="json"))
    return tasks


def technical_task_chain() -> RunnableLambda:
    """Offline structured transformation; it performs no LLM or network call."""
    return RunnableLambda(_compose)
