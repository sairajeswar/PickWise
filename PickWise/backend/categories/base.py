"""
Base interfaces and classes for extensible product categories in PickWise.
New categories (Laptops, TVs, etc.) can subclass or configure Category.
"""

from typing import Dict, List, Any, Optional

class MetricDefinition:
    def __init__(
        self,
        key: str,
        name: str,
        category_group: str,
        higher_is_better: bool = True,
        default_weight: float = 0.0,
        unit: str = "",
        description: str = ""
    ):
        self.key = key
        self.name = name
        self.category_group = category_group
        self.higher_is_better = higher_is_better
        self.default_weight = default_weight
        self.unit = unit
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "name": self.name,
            "category_group": self.category_group,
            "higher_is_better": self.higher_is_better,
            "default_weight": self.default_weight,
            "unit": self.unit,
            "description": self.description
        }


class BaseCategory:
    category_id: str = "generic"
    name: str = "Generic Product"
    groups: Dict[str, str] = {}
    default_group_weights: Dict[str, float] = {}
    presets: Dict[str, Dict[str, float]] = {}
    metrics: List[MetricDefinition] = []

    @classmethod
    def get_groups(cls) -> Dict[str, str]:
        return cls.groups

    @classmethod
    def get_default_weights(cls) -> Dict[str, float]:
        return cls.default_group_weights

    @classmethod
    def get_presets(cls) -> Dict[str, Dict[str, float]]:
        return cls.presets

    @classmethod
    def get_metrics(cls) -> List[MetricDefinition]:
        return cls.metrics

    @classmethod
    def parse_numeric_metric(cls, key: str, value: Any) -> Optional[float]:
        """Convert raw spec value to numeric metric for scoring."""
        raise NotImplementedError
