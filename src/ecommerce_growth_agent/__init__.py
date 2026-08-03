"""Offline e-commerce growth analysis agent."""

from .agent import GrowthAgent
from .config import BusinessThresholds, load_thresholds

__all__ = ["BusinessThresholds", "GrowthAgent", "load_thresholds"]
__version__ = "0.3.0"
