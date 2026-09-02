"""Offline e-commerce growth analysis agent."""

from .agent import GrowthAgent
from .config import BusinessThresholds, load_thresholds
from .history import AnalysisHistoryStore, RetentionPolicy, fingerprint_rows
from .explanation import DeterministicExplanationAdapter, ExplanationAdapter, explain_report
from .service_contract import analyze_request
from .request_receipt import build_request_receipt
from .observability import summarize_request_observability
from .service_response import validate_service_response

__all__ = [
    "AnalysisHistoryStore",
    "BusinessThresholds",
    "DeterministicExplanationAdapter",
    "ExplanationAdapter",
    "GrowthAgent",
    "RetentionPolicy",
    "fingerprint_rows",
    "explain_report",
    "load_thresholds",
    "analyze_request",
    "build_request_receipt",
    "summarize_request_observability",
    "validate_service_response",
]
__version__ = "1.0.0"
