"""
Generates deterministic plain-language explanations for PickWise:
- 3 to 4 winning reasons for the champion product
- "Why not the others?" line for each non-winner product
"""

from typing import List, Dict, Any

class ReasonGenerator:
    @staticmethod
    def generate_winner_reasons(
        winner: Dict[str, Any],
        all_scored: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Derives 3 to 4 prominent reasons why the top product won.
        """
        reasons = []
        w_specs = winner.get("specs", {})
        w_groups = winner.get("group_scores", {})
        
        # 1. Price / Value reason
        price_group = w_groups.get("price", {})
        if price_group.get("score_pct", 0) >= 80:
            prices = [p["specs"].get("price") for p in all_scored if p["specs"].get("price")]
            if prices and min(prices) == w_specs.get("price"):
                reasons.append(f"Most budget-friendly choice at ₹{int(w_specs.get('price')):,}, providing highest spec-per-rupee value.")
            else:
                reasons.append(f"Highly competitive pricing at ₹{int(w_specs.get('price', 0)):,} with balanced feature set.")

        # 2. Performance reason
        perf_group = w_groups.get("performance", {})
        if perf_group.get("score_pct", 0) >= 75:
            chip = winner.get("matched_chipset") or w_specs.get("chipset") or "Fast Processor"
            reasons.append(f"Superior performance powered by {chip} for smooth gaming and heavy multitasking.")

        # 3. Battery / Charging reason
        battery_group = w_groups.get("battery", {})
        if battery_group.get("score_pct", 0) >= 70:
            mah = w_specs.get("battery_capacity")
            w = w_specs.get("charging_speed")
            if mah and w:
                reasons.append(f"Reliable all-day stamina with {mah}mAh battery and rapid {w}W fast charging.")
            elif mah:
                reasons.append(f"Hefty {mah}mAh battery ensures extended screen-on duration.")

        # 4. Camera reason
        cam_group = w_groups.get("camera", {})
        if cam_group.get("score_pct", 0) >= 70:
            rc = w_specs.get("rear_camera")
            fc = w_specs.get("front_camera")
            reasons.append(f"Crisp camera setup with {rc}MP primary sensor and {fc}MP selfie shooter.")

        # 5. Display reason
        disp_group = w_groups.get("display", {})
        if disp_group.get("score_pct", 0) >= 70:
            hz = w_specs.get("refresh_rate")
            dtype = w_specs.get("display_type", "")
            reasons.append(f"Vibrant and fluid visual experience with {hz}Hz {dtype} display.")

        # 6. Community approval / rating
        rating_group = w_groups.get("ratings", {})
        if rating_group.get("score_pct", 0) >= 75:
            r = w_specs.get("rating")
            rc = w_specs.get("review_count")
            if r and rc:
                reasons.append(f"Trusted user feedback: rated {r}/5 across {rc:,} verified buyer reviews.")

        # If fewer than 3 reasons, add general balance statements
        if len(reasons) < 3:
            reasons.append("Maintains consistent strength across all test categories without severe bottlenecks.")
        if len(reasons) < 3:
            reasons.append(f"Achieved the highest aggregate benchmark score ({winner['total_score']}/100) based on your chosen weights.")

        return reasons[:4]

    @staticmethod
    def generate_why_not_others(
        all_scored: List[Dict[str, Any]],
        winner: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generates concise 'Why not this one?' explanations for each non-winner.
        """
        why_not_list = []
        w_specs = winner.get("specs", {})
        w_groups = winner.get("group_scores", {})
        w_price = w_specs.get("price")

        for product in all_scored:
            if product["product_id"] == winner["product_id"]:
                continue

            specs = product.get("specs", {})
            groups = product.get("group_scores", {})
            price = specs.get("price")

            reasons = []

            # Price comparison
            if price and w_price and price > w_price:
                diff = int(price - w_price)
                if diff > 1000:
                    reasons.append(f"Priced ₹{diff:,} higher without offering proportional spec gains")

            # Weakest category relative to winner
            worst_gap = 0.0
            worst_group_name = ""
            for g_key, g_info in groups.items():
                w_score = w_groups.get(g_key, {}).get("score_pct") or 0.0
                curr_score = g_info.get("score_pct") or 0.0
                gap = w_score - curr_score
                if gap > worst_gap:
                    worst_gap = gap
                    worst_group_name = g_info.get("group_name", g_key)

            if worst_gap >= 15.0 and worst_group_name:
                reasons.append(f"Significantly trails in {worst_group_name}")

            # Missing key specs
            missing = product.get("missing_metrics", [])
            if len(missing) >= 2:
                names = [m["name"] for m in missing[:2]]
                reasons.append(f"Lacks verified data for {', '.join(names)}")

            # Specific hardware disadvantages
            w_bench = winner.get("group_scores", {}).get("performance", {}).get("score_pct", 0)
            curr_bench = groups.get("performance", {}).get("score_pct", 0)
            if w_bench - curr_bench > 25:
                reasons.append("Noticeably lower processor benchmark limits gaming longevity")

            w_bat = w_specs.get("battery_capacity")
            curr_bat = specs.get("battery_capacity")
            if w_bat and curr_bat and (w_bat - curr_bat) >= 500:
                reasons.append(f"Smaller battery capacity ({curr_bat}mAh vs {w_bat}mAh)")

            if not reasons:
                reasons.append(f"Scored {round(winner['total_score'] - product['total_score'], 1)} points lower in overall weighted score")

            primary_reason = ". ".join(reasons[:2]) + "."

            why_not_list.append({
                "product_id": product["product_id"],
                "name": product["name"],
                "rank": product["rank"],
                "total_score": product["total_score"],
                "explanation": primary_reason
            })

        return why_not_list
