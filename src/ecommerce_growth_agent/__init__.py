"""Offline e-commerce growth analysis agent."""

from .agent import GrowthAgent
from .config import BusinessThresholds, load_thresholds
from .history import AnalysisHistoryStore, RetentionPolicy, fingerprint_rows

__all__ = [
    "AnalysisHistoryStore",
    "BusinessThresholds",
    "GrowthAgent",
    "RetentionPolicy",
    "fingerprint_rows",
    "load_thresholds",
]
__version__ = "0.4.0"
