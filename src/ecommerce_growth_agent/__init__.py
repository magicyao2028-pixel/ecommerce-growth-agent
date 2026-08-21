"""Offline e-commerce growth analysis agent."""

from .agent import GrowthAgent
from .config import BusinessThresholds, load_thresholds
from .history import AnalysisHistoryStore, RetentionPolicy, fingerprint_rows
from .explanation import DeterministicExplanationAdapter, ExplanationAdapter, explain_report

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
]
__version__ = "0.6.0"
