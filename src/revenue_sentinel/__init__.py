"""Revenue Sentinel: evidence-first opportunity triage."""

from .engine import AuditEngine
from .models import AuditResult, Opportunity

__all__ = ["AuditEngine", "AuditResult", "Opportunity"]
__version__ = "0.1.0"
