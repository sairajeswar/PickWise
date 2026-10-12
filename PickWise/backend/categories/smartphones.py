import json
import os
import re
from typing import Dict, Any, Optional, Tuple
from .base import BaseCategory, MetricDefinition

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CHIPSET_PATH = os.path.join(DATA_DIR, "chipsets.json")

def load_chipset_db() -> Dict[str, Any]:
    try:
        if os.path.exists(CHIPSET_PATH):
            with open(CHIPSET_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("chipsets", {})
    except Exception:
        pass
    return {}

CHIPSET_DB = load_chipset_db()

class SmartphoneCategory(BaseCategory):
    category_id = "smartphones"
    name = "Smartphones"

    groups = {
        "price": "Price & Value",
        "performance": "Performance",
        "camera": "Camera System",
        "battery": "Battery & Charging",
        "display": "Display Quality",
        "storage": "RAM & Storage",
        "ratings": "User Ratings"
    }

    default_group_weights = {
        "price": 25.0,
        "performance": 20.0,
        "camera": 15.0,
        "battery": 15.0,
        "display": 10.0,
        "storage": 10.0,
        "ratings": 5.0
    }

    presets = {
        "Balanced": {
            "price": 25.0,
            "performance": 20.0,
            "camera": 15.0,
            "battery": 15.0,
            "display": 10.0,
            "storage": 10.0,
            "ratings": 5.0
        },
        "Gaming": {
            "price": 10.0,
            "performance": 35.0,
            "camera": 5.0,
            "battery": 20.0,
            "display": 15.0,
            "storage": 10.0,
            "ratings": 5.0
        },
        "Camera": {
            "price": 15.0,
            "performance": 15.0,
            "camera": 35.0,
            "battery": 10.0,
            "display": 15.0,
            "storage": 5.0,
            "ratings": 5.0
        },
        "Battery": {
            "price": 20.0,
            "performance": 10.0,
            "camera": 5.0,
            "battery": 40.0,
            "display": 10.0,
            "storage": 10.0,
            "ratings": 5.0
        },
        "Budget": {
            "price": 45.0,
            "performance": 15.0,
            "camera": 10.0,
            "battery": 15.0,
            "display": 5.0,
            "storage": 5.0,
            "ratings": 5.0
        }
    }

    metrics = [
        MetricDefinition("price", "Effective Price", "price", higher_is_better=False, default_weight=25.0, unit="₹"),
        MetricDefinition("performance", "Processor Benchmark", "performance", higher_is_better=True, default_weight=20.0, unit="/100"),
        MetricDefinition("rear_camera", "Rear Primary Camera", "camera", higher_is_better=True, default_weight=10.0, unit="MP"),
        MetricDefinition("front_camera", "Front Camera", "camera", higher_is_better=True, default_weight=5.0, unit="MP"),
        MetricDefinition("battery_capacity", "Battery Capacity", "battery", higher_is_better=True, default_weight=10.0, unit="mAh"),
        MetricDefinition("charging_speed", "Charging Speed", "battery", higher_is_better=True, default_weight=5.0, unit="W"),
        MetricDefinition("refresh_rate", "Display Refresh Rate", "display", higher_is_better=True, default_weight=5.0, unit="Hz"),
        MetricDefinition("display_score", "Display Tech & Size", "display", higher_is_better=True, default_weight=5.0, unit="pts"),
        MetricDefinition("ram", "RAM Capacity", "storage", higher_is_better=True, default_weight=5.0, unit="GB"),
        MetricDefinition("storage", "Internal Storage", "storage", higher_is_better=True, default_weight=5.0, unit="GB"),
        MetricDefinition("bayesian_rating", "Community Rating", "ratings", higher_is_better=True, default_weight=5.0, unit="/5.0")
    ]

    @classmethod
    def resolve_chipset_score(cls, chipset_name: Optional[str]) -> Tuple[Optional[float], bool, str]:
        """
        Returns (score, is_approximate, matched_name).
        Matches against local chipsets.json.
        """
        if not chipset_name or not isinstance(chipset_name, str):
            return (None, True, "Unknown")
        
        cleaned = chipset_name.lower().strip()
        cleaned = re.sub(r'[\(\)\[\],]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Direct exact match
        for key, data in CHIPSET_DB.items():
            if key == cleaned:
                return (float(data["score"]), False, key.title())

        # Substring / token matching
        best_match = None
        best_len = 0
        for key, data in CHIPSET_DB.items():
            # Check if key words are in cleaned or vice versa
            if key in cleaned:
                if len(key) > best_len:
                    best_match = (float(data["score"]), False, key.title())
                    best_len = len(key)
        
        if best_match:
            return best_match

        # Fuzzy heuristic fallback for newer or variant chipsets
        if "8 elite" in cleaned:
            return (99.0, True, "Snapdragon 8 Elite (Est)")
        if "9400" in cleaned:
            return (97.0, True, "Dimensity 9400 (Est)")
        if "a18" in cleaned:
            return (96.0, True, "Apple A18 (Est)")
        if "gen 3" in cleaned or "8 gen 3" in cleaned:
            return (90.0, True, "Snapdragon 8 Gen 3 Class (Est)")
        if "gen 2" in cleaned:
            return (80.0, True, "Snapdragon 8 Gen 2 Class (Est)")
        if "gen 1" in cleaned:
            return (70.0, True, "Snapdragon 8 Gen 1 Class (Est)")
        if "dimensity 9" in cleaned:
            return (85.0, True, "Dimensity 9000 Class (Est)")
        if "dimensity 8" in cleaned:
            return (72.0, True, "Dimensity 8000 Class (Est)")
        if "dimensity 7" in cleaned:
            return (55.0, True, "Dimensity 7000 Class (Est)")
        if "dimensity 6" in cleaned:
            return (42.0, True, "Dimensity 6000 Class (Est)")
        if "snapdragon 7" in cleaned:
            return (60.0, True, "Snapdragon 7 Series (Est)")
        if "snapdragon 6" in cleaned or "695" in cleaned:
            return (45.0, True, "Snapdragon 6 Series (Est)")
        if "snapdragon 4" in cleaned:
            return (40.0, True, "Snapdragon 4 Series (Est)")
        if "bionic" in cleaned or "apple a" in cleaned:
            return (80.0, True, "Apple A-Series (Est)")
        if "tensor" in cleaned:
            return (75.0, True, "Google Tensor (Est)")
        if "helio" in cleaned or "unisoc" in cleaned:
            return (32.0, True, "Entry Level (Est)")

        return (50.0, True, f"Generic Octa-Core ({chipset_name[:20]})")

    @classmethod
    def calculate_display_score(cls, size_inch: Optional[float], display_type: Optional[str]) -> Optional[float]:
        """Calculates display score from size and panel tech (AMOLED/OLED vs LCD)."""
        if size_inch is None and display_type is None:
            return None
        score = 50.0
        if size_inch:
            # Ideal phone range is around 6.5 - 6.8 inches
            score += min(max((size_inch - 6.0) * 15, 0), 20)
        if display_type:
            d_type = display_type.lower()
            if any(term in d_type for term in ["amoled", "oled", "super amoled", "dynamic amoled", "retina"]):
                score += 30.0
            elif "ips" in d_type:
                score += 15.0
            elif "lcd" in d_type:
                score += 10.0
        return min(score, 100.0)

    @classmethod
    def calculate_bayesian_rating(cls, rating: Optional[float], review_count: Optional[int]) -> Optional[float]:
        """
        Bayesian weighted rating:
        WR = (v / (v + m)) * R + (m / (v + m)) * C
        v = review count, m = 100 (threshold), C = 4.0 (prior mean), R = rating
        """
        if rating is None:
            return None
        v = float(review_count) if review_count and review_count > 0 else 10.0
        m = 100.0
        c = 4.0
        return round(((v / (v + m)) * rating) + ((m / (v + m)) * c), 3)
