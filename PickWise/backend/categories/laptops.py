"""
Demonstration of PickWise category extensibility: Laptop configuration.
"""
from typing import Dict, Any, Optional
from .base import BaseCategory, MetricDefinition

class LaptopCategory(BaseCategory):
    category_id = "laptops"
    name = "Laptops"

    groups = {
        "price": "Price & Value",
        "performance": "CPU & GPU Power",
        "battery": "Battery Life",
        "display": "Screen & Resolution",
        "storage": "RAM & SSD Capacity",
        "portability": "Weight & Form Factor"
    }

    default_group_weights = {
        "price": 25.0,
        "performance": 30.0,
        "battery": 15.0,
        "display": 15.0,
        "storage": 10.0,
        "portability": 5.0
    }

    presets = {
        "Balanced": default_group_weights,
        "Gaming": {
            "price": 15.0,
            "performance": 45.0,
            "display": 20.0,
            "storage": 10.0,
            "battery": 5.0,
            "portability": 5.0
        },
        "Productivity": {
            "price": 20.0,
            "performance": 25.0,
            "battery": 25.0,
            "display": 15.0,
            "storage": 10.0,
            "portability": 5.0
        }
    }

    metrics = [
        MetricDefinition("price", "Effective Price", "price", higher_is_better=False, default_weight=25.0, unit="₹"),
        MetricDefinition("cpu_benchmark", "CPU Benchmark", "performance", higher_is_better=True, default_weight=20.0, unit="pts"),
        MetricDefinition("ram", "RAM Capacity", "storage", higher_is_better=True, default_weight=5.0, unit="GB"),
        MetricDefinition("storage", "SSD Capacity", "storage", higher_is_better=True, default_weight=5.0, unit="GB"),
        MetricDefinition("battery_hours", "Battery Life", "battery", higher_is_better=True, default_weight=15.0, unit="hrs"),
        MetricDefinition("display_res", "Display Resolution", "display", higher_is_better=True, default_weight=15.0, unit="p"),
        MetricDefinition("weight_kg", "Portability Weight", "portability", higher_is_better=False, default_weight=5.0, unit="kg")
    ]
