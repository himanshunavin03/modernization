"""Explicit design-to-requirement conflict handling; requirements always win."""
from __future__ import annotations

from .models import DesignRequirementConflict, DesignSpecification


def detect_design_conflicts(design: DesignSpecification, approved_requirement_ids: set[str]) -> DesignSpecification:
    conflicts = []
    unresolved = list(design.unresolved_items)
    for link in design.requirement_links:
        if link.requirement_ref not in approved_requirement_ids:
            unresolved.append(f"Design link {link.design_ref} references unknown requirement {link.requirement_ref}.")
        elif link.relationship == "CONFLICTS":
            conflicts.append(DesignRequirementConflict(
                design_reference=link.design_ref,
                requirement_reference=link.requirement_ref,
                conflict_description=link.description,
                required_clarification="Resolve the presentation conflict without changing the approved requirement.",
            ))
    return design.model_copy(update={"conflicts": conflicts, "unresolved_items": unresolved})
