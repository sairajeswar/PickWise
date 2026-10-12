"""
Spec comparison grid generator.
Tags each spec value across products and identifies which product holds the best value in each row.
"""

from typing import List, Dict, Any, Optional

SPEC_ROWS_CONFIG = [
    {"key": "price", "label": "Price", "unit": "₹", "higher_is_better": False, "format": "currency"},
    {"key": "mrp", "label": "MRP", "unit": "₹", "higher_is_better": False, "format": "currency"},
    {"key": "discount_pct", "label": "Discount", "unit": "%", "higher_is_better": True, "format": "number"},
    {"key": "chipset", "label": "Processor / Chipset", "unit": "", "higher_is_better": None, "format": "chipset"},
    {"key": "performance_score", "label": "Benchmark Tier", "unit": "/100", "higher_is_better": True, "format": "number"},
    {"key": "ram", "label": "RAM", "unit": "GB", "higher_is_better": True, "format": "number"},
    {"key": "storage", "label": "Storage", "unit": "GB", "higher_is_better": True, "format": "number"},
    {"key": "rear_camera", "label": "Rear Camera", "unit": "MP", "higher_is_better": True, "format": "number"},
    {"key": "front_camera", "label": "Front Camera", "unit": "MP", "higher_is_better": True, "format": "number"},
    {"key": "battery_capacity", "label": "Battery", "unit": "mAh", "higher_is_better": True, "format": "number"},
    {"key": "charging_speed", "label": "Charging Speed", "unit": "W", "higher_is_better": True, "format": "number"},
    {"key": "display_size", "label": "Screen Size", "unit": "inches", "higher_is_better": True, "format": "number"},
    {"key": "refresh_rate", "label": "Refresh Rate", "unit": "Hz", "higher_is_better": True, "format": "number"},
    {"key": "display_type", "label": "Display Type", "unit": "", "higher_is_better": None, "format": "text"},
    {"key": "rating", "label": "Rating", "unit": "★", "higher_is_better": True, "format": "rating"},
    {"key": "review_count", "label": "Reviews", "unit": "", "higher_is_better": True, "format": "number"},
    {"key": "os", "label": "Operating System", "unit": "", "higher_is_better": None, "format": "text"}
]

class ComparisonTableBuilder:
    @staticmethod
    def build_comparison_table(scored_products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Builds side-by-side spec comparison rows with 'is_best' flag for each cell.
        """
        table_rows = []

        for row_cfg in SPEC_ROWS_CONFIG:
            key = row_cfg["key"]
            label = row_cfg["label"]
            unit = row_cfg["unit"]
            higher_is_better = row_cfg["higher_is_better"]
            fmt = row_cfg["format"]

            cells = []
            numeric_values = []

            for p in scored_products:
                specs = p.get("specs", {})
                
                # Fetch raw and numeric value
                if key == "performance_score":
                    raw_val = p.get("group_scores", {}).get("performance", {}).get("score_pct")
                    num_val = float(raw_val) if raw_val is not None else None
                elif key == "chipset":
                    raw_val = specs.get("chipset") or p.get("matched_chipset")
                    num_val = None
                else:
                    raw_val = specs.get(key)
                    try:
                        num_val = float(raw_val) if raw_val is not None else None
                    except (ValueError, TypeError):
                        num_val = None

                display_text = ComparisonTableBuilder._format_value(raw_val, fmt, unit)
                cells.append({
                    "product_id": p["product_id"],
                    "raw_value": raw_val,
                    "numeric_value": num_val,
                    "display_text": display_text,
                    "is_best": False
                })

                if num_val is not None:
                    numeric_values.append(num_val)

            # Determine best value(s) in this row if comparable
            if higher_is_better is not None and numeric_values:
                target_val = max(numeric_values) if higher_is_better else min(numeric_values)
                # Only highlight if not all are tied or single
                if len(set(numeric_values)) > 1:
                    for cell in cells:
                        if cell["numeric_value"] is not None and cell["numeric_value"] == target_val:
                            cell["is_best"] = True

            table_rows.append({
                "key": key,
                "label": label,
                "unit": unit,
                "higher_is_better": higher_is_better,
                "cells": cells
            })

        return table_rows

    @staticmethod
    def _format_value(val: Any, fmt: str, unit: str) -> str:
        if val is None or val == "" or str(val).lower() == "none":
            return "N/A"

        try:
            if fmt == "currency":
                num = int(float(val))
                return f"₹{num:,}"
            elif fmt == "rating":
                return f"{float(val):.1f} / 5"
            elif fmt == "number":
                num = float(val)
                if num.is_integer():
                    return f"{int(num):,} {unit}".strip()
                return f"{num} {unit}".strip()
        except Exception:
            pass

        return f"{val} {unit}".strip() if unit else str(val)
