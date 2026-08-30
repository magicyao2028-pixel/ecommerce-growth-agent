"""Offline e-commerce growth analysis agent."""

from .agent import GrowthAgent
from .config import BusinessThresholds, load_thresholds
from .history import AnalysisHistoryStore, RetentionPolicy, fingerprint_rows
from .explanation import DeterministicExplanationAdapter, ExplanationAdapter, explain_report
from .service_contract import analyze_request
from .request_receipt import build_request_receipt
from .observability import summarize_request_observability

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
]
__version__ = "0.9.0"
