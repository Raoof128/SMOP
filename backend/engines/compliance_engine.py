"""Compliance reporting and governance mapping."""

from __future__ import annotations

from typing import Dict, List

from backend.utils.logger import audit_event, get_logger

logger = get_logger(__name__)

FRAMEWORK_MAPPING = {
    "NIST_AI_RMF": ["Govern", "Map", "Measure", "Manage"],
    "ISO_42001": ["Context", "Leadership", "Planning", "Support", "Operation"],
    "ACSC_E8": ["Application Control", "Patch Management", "Logging"],
    "Privacy_Act_ADM": ["Data_Minimization", "Transparency"],
}


class ComplianceEngine:
    """Produces compliance events and mappings."""

    def record_event(self, domain: str, detail: str) -> Dict[str, List[str]]:
        """Record a compliance event mapped to relevant governance frameworks."""

        mapping = FRAMEWORK_MAPPING.get(domain, [])
        audit_event("compliance", domain, detail)
        return {"domain": domain, "controls": mapping, "detail": detail}
