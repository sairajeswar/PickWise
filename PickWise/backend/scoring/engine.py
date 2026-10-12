"""
PickWise Deterministic Scoring Engine.
Calculates transparent, mathematical multi-criteria scores across products.
Handles missing data with dynamic weight redistribution and confidence scoring.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.categories.smartphones import SmartphoneCategory
from backend.categories.base import BaseCategory

class ScoringEngine:
    def __init__(self, category: BaseCategory = SmartphoneCategory):
        self.category = category

    def score_products(
        self,
        products: List[Dict[str, Any]],
        user_group_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculates scores for a list of products (2 to 5).
        """
        if not products or len(products) < 2:
            raise ValueError("Comparison requires at least 2 products.")
        if len(products) > 5:
            raise ValueError("Comparison supports at most 5 products.")

        # Determine effective group weights (normalized so sum of group weights = 100)
        group_weights = self._normalize_group_weights(user_group_weights)
        
        # Determine weights for individual metrics within each group
        metric_weights = self._distribute_metric_weights(group_weights)

        # Pre-process raw product specs into numeric metrics
        processed_products = []
        for p in products:
            proc = self._preprocess_specs(p)
            processed_products.append(proc)

        # Compute min & max for each metric across this specific batch
        metric_bounds = self._calculate_metric_bounds(processed_products)

        # Score each product
        scored_products = []
        for proc in processed_products:
            score_data = self._calculate_product_score(proc, metric_bounds, metric_weights, group_weights)
            scored_products.append(score_data)

        # Sort products by total score descending
        scored_products.sort(key=lambda x: x["total_score"], reverse=True)

        # Assign ranks
        for idx, sp in enumerate(scored_products):
            sp["rank"] = idx + 1

        # Check for close call between rank 1 and 2
        close_call_info = self._check_close_call(scored_products)

        # Determine category-wise winners
        category_winners = self._determine_category_winners(scored_products, group_weights)

        return {
            "scored_products": scored_products,
            "metric_bounds": metric_bounds,
            "group_weights": group_weights,
            "close_call": close_call_info,
            "category_winners": category_winners
        }

    def _normalize_group_weights(self, weights: Optional[Dict[str, float]]) -> Dict[str, float]:
        default_weights = self.category.get_default_weights()
        if not weights:
            return dict(default_weights)
        
        # Merge with defaults for any missing keys
        merged = {}
        for k in default_weights.keys():
            merged[k] = float(weights.get(k, default_weights[k]))

        total = sum(merged.values())
        if total <= 0:
            return dict(default_weights)

        # Normalize to sum to 100.0
        return {k: round((v / total) * 100.0, 2) for k, v in merged.items()}

    def _distribute_metric_weights(self, group_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Distributes group weights equally or proportionally among metrics belonging to that group.
        """
        metrics = self.category.get_metrics()
        group_to_metrics = {}
        for m in metrics:
            group_to_metrics.setdefault(m.category_group, []).append(m)

        metric_weights = {}
        for group, m_list in group_to_metrics.items():
            g_weight = group_weights.get(group, 0.0)
            if not m_list:
                continue
            
            # Check if metrics have relative default_weight
            sum_default = sum(m.default_weight for m in m_list)
            if sum_default > 0:
                for m in m_list:
                    metric_weights[m.key] = (m.default_weight / sum_default) * g_weight
            else:
                share = g_weight / len(m_list)
                for m in m_list:
                    metric_weights[m.key] = share

        return metric_weights

    def _preprocess_specs(self, raw_product: Dict[str, Any]) -> Dict[str, Any]:
        """Extracts and standardizes numeric values from raw product dictionary."""
        specs = raw_product.get("specs", {})
        proc = {
            "id": raw_product.get("id") or raw_product.get("url") or raw_product.get("name"),
            "name": raw_product.get("name", "Unknown Product"),
            "brand": raw_product.get("brand", "Unknown"),
            "url": raw_product.get("url", ""),
            "image": raw_product.get("image", ""),
            "price": self._to_float(specs.get("price")),
            "mrp": self._to_float(specs.get("mrp")),
            "discount_pct": self._to_float(specs.get("discount_pct")),
            "rating": self._to_float(specs.get("rating")),
            "review_count": self._to_int(specs.get("review_count")),
            "ram": self._to_float(specs.get("ram")),
            "storage": self._to_float(specs.get("storage")),
            "chipset": specs.get("chipset"),
            "battery_capacity": self._to_float(specs.get("battery_capacity")),
            "charging_speed": self._to_float(specs.get("charging_speed")),
            "rear_camera": self._to_float(specs.get("rear_camera")),
            "front_camera": self._to_float(specs.get("front_camera")),
            "refresh_rate": self._to_float(specs.get("refresh_rate")),
            "display_size": self._to_float(specs.get("display_size")),
            "display_type": specs.get("display_type", ""),
            "raw_specs": specs
        }

        # Resolve performance benchmark score
        bench_score, is_approx, matched_chip = SmartphoneCategory.resolve_chipset_score(proc["chipset"])
        proc["performance"] = bench_score
        proc["chipset_approximate"] = is_approx
        proc["matched_chipset"] = matched_chip

        # Resolve display score
        proc["display_score"] = SmartphoneCategory.calculate_display_score(proc["display_size"], proc["display_type"])

        # Resolve Bayesian rating
        proc["bayesian_rating"] = SmartphoneCategory.calculate_bayesian_rating(proc["rating"], proc["review_count"])

        return proc

    def _to_float(self, val: Any) -> Optional[float]:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return float(val)
        try:
            cleaned = str(val).replace(",", "").replace("₹", "").replace("$", "").strip()
            # Extract first float/int match
            import re
            m = re.search(r'\d+(\.\d+)?', cleaned)
            if m:
                return float(m.group(0))
        except Exception:
            pass
        return None

    def _to_int(self, val: Any) -> Optional[int]:
        f = self._to_float(val)
        return int(f) if f is not None else None

    def _calculate_metric_bounds(self, processed_products: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        metrics = self.category.get_metrics()
        bounds = {}
        for m in metrics:
            vals = [p.get(m.key) for p in processed_products if p.get(m.key) is not None]
            if vals:
                bounds[m.key] = {
                    "min": min(vals),
                    "max": max(vals),
                    "count": len(vals)
                }
            else:
                bounds[m.key] = {"min": 0.0, "max": 0.0, "count": 0}
        return bounds

    def _calculate_product_score(
        self,
        product: Dict[str, Any],
        bounds: Dict[str, Dict[str, float]],
        metric_weights: Dict[str, float],
        group_weights: Dict[str, float]
    ) -> Dict[str, Any]:
        metrics = self.category.get_metrics()
        total_possible_weight = 0.0
        accumulated_score = 0.0
        metric_breakdowns = []
        missing_metrics = []
        group_scores = {g: {"score": 0.0, "total_weight": 0.0, "earned_weight": 0.0} for g in group_weights}

        for m in metrics:
            val = product.get(m.key)
            w = metric_weights.get(m.key, 0.0)
            if w <= 0:
                continue

            if val is None:
                missing_metrics.append({
                    "key": m.key,
                    "name": m.name,
                    "lost_weight": round(w, 2)
                })
                continue

            b = bounds.get(m.key, {"min": 0.0, "max": 0.0})
            min_val = b["min"]
            max_val = b["max"]

            # Min-Max Normalization
            if max_val == min_val:
                norm_score = 1.0  # Tied / identical values get full score
            else:
                if m.higher_is_better:
                    norm_score = (val - min_val) / (max_val - min_val)
                else:
                    norm_score = (max_val - val) / (max_val - min_val)

            norm_score = max(0.0, min(1.0, norm_score))
            points_earned = norm_score * w

            accumulated_score += points_earned
            total_possible_weight += w

            # Group accumulation
            g = m.category_group
            if g in group_scores:
                group_scores[g]["total_weight"] += w
                group_scores[g]["earned_weight"] += points_earned

            metric_breakdowns.append({
                "key": m.key,
                "name": m.name,
                "group": m.category_group,
                "raw_value": val,
                "unit": m.unit,
                "higher_is_better": m.higher_is_better,
                "min_batch": min_val,
                "max_batch": max_val,
                "norm_score": round(norm_score, 4),
                "weight": round(w, 2),
                "points_earned": round(points_earned, 2)
            })

        # Dynamic weight redistribution: scale to 100
        if total_possible_weight > 0:
            final_total_score = round((accumulated_score / total_possible_weight) * 100.0, 1)
            confidence_pct = round((total_possible_weight / 100.0) * 100.0, 1)
        else:
            final_total_score = 0.0
            confidence_pct = 0.0

        is_low_confidence = confidence_pct < 80.0 or len(missing_metrics) >= 3

        # Form group summary percentages
        formatted_group_scores = {}
        for g_key, g_data in group_scores.items():
            if g_data["total_weight"] > 0:
                g_pct = round((g_data["earned_weight"] / g_data["total_weight"]) * 100.0, 1)
            else:
                g_pct = None
            formatted_group_scores[g_key] = {
                "score_pct": g_pct,
                "weight": group_weights.get(g_key, 0.0),
                "group_name": self.category.get_groups().get(g_key, g_key.title())
            }

        return {
            "product_id": product["id"],
            "name": product["name"],
            "brand": product["brand"],
            "url": product["url"],
            "image": product["image"],
            "specs": product["raw_specs"],
            "total_score": final_total_score,
            "confidence_pct": confidence_pct,
            "is_low_confidence": is_low_confidence,
            "missing_metrics": missing_metrics,
            "chipset_approximate": product.get("chipset_approximate", False),
            "matched_chipset": product.get("matched_chipset", ""),
            "group_scores": formatted_group_scores,
            "metric_breakdowns": metric_breakdowns
        }

    def _check_close_call(self, scored_products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detects if top 2 products are within 3.0 points."""
        if len(scored_products) < 2:
            return {"is_close_call": False}

        p1 = scored_products[0]
        p2 = scored_products[1]
        diff = round(p1["total_score"] - p2["total_score"], 1)

        if diff <= 3.0:
            # Find deciding factor between p1 and p2
            factor = self._find_deciding_factor(p1, p2)
            return {
                "is_close_call": True,
                "score_difference": diff,
                "product1_name": p1["name"],
                "product2_name": p2["name"],
                "deciding_factor": factor,
                "recommendation": f"Very close race ({diff} pts gap). Choose {p1['name']} if you prioritize {factor['p1_advantage']}, or {p2['name']} for {factor['p2_advantage']}."
            }

        return {"is_close_call": False, "score_difference": diff}

    def _find_deciding_factor(self, p1: Dict[str, Any], p2: Dict[str, Any]) -> Dict[str, str]:
        """Identifies key distinguishing areas between top 2 contestants."""
        advantages_p1 = []
        advantages_p2 = []

        g1 = p1.get("group_scores", {})
        g2 = p2.get("group_scores", {})

        for g_key in g1.keys():
            s1 = g1[g_key]["score_pct"] or 0.0
            s2 = g2[g_key]["score_pct"] or 0.0
            g_name = g1[g_key]["group_name"]
            if s1 - s2 > 10.0:
                advantages_p1.append(g_name)
            elif s2 - s1 > 10.0:
                advantages_p2.append(g_name)

        p1_adv = ", ".join(advantages_p1[:2]) if advantages_p1 else "overall balance"
        p2_adv = ", ".join(advantages_p2[:2]) if advantages_p2 else "value"
        return {"p1_advantage": p1_adv, "p2_advantage": p2_adv}

    def _determine_category_winners(
        self,
        scored_products: List[Dict[str, Any]],
        group_weights: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identifies the clear winner for each category group."""
        category_winners = []
        groups = self.category.get_groups()

        for g_key, g_title in groups.items():
            best_product = None
            best_score = -1.0
            for sp in scored_products:
                g_info = sp["group_scores"].get(g_key, {})
                s = g_info.get("score_pct")
                if s is not None and s > best_score:
                    best_score = s
                    best_product = sp

            if best_product and best_score >= 0:
                # Find winning spec value to display in the table
                winning_detail = self._extract_group_winning_detail(best_product, g_key)
                category_winners.append({
                    "group_key": g_key,
                    "group_name": g_title,
                    "winner_id": best_product["product_id"],
                    "winner_name": best_product["name"],
                    "winner_score": best_score,
                    "detail": winning_detail
                })

        return category_winners

    def _extract_group_winning_detail(self, product: Dict[str, Any], group_key: str) -> str:
        specs = product.get("specs", {})
        if group_key == "price":
            p = specs.get("price")
            return f"₹{int(p):,}" if p else "Lowest Price"
        elif group_key == "performance":
            return product.get("matched_chipset") or specs.get("chipset") or "High Benchmark"
        elif group_key == "camera":
            rc = specs.get("rear_camera")
            fc = specs.get("front_camera")
            return f"{rc}MP Rear / {fc}MP Front" if rc else "Top Camera System"
        elif group_key == "battery":
            mah = specs.get("battery_capacity")
            w = specs.get("charging_speed")
            return f"{mah}mAh + {w}W Fast Charge" if (mah and w) else f"{mah}mAh"
        elif group_key == "display":
            hz = specs.get("refresh_rate")
            sz = specs.get("display_size")
            dtype = specs.get("display_type", "")
            return f"{sz}\" {hz}Hz {dtype}".strip()
        elif group_key == "storage":
            ram = specs.get("ram")
            rom = specs.get("storage")
            return f"{ram}GB RAM / {rom}GB Storage"
        elif group_key == "ratings":
            r = specs.get("rating")
            rc = specs.get("review_count")
            return f"{r}/5 ({rc:,} reviews)" if (r and rc) else f"{r}/5"
        return "Top Performer"
