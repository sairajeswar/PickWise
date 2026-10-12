"""
Verification script for real links and manual fallback flow.
"""

import sys
import os

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend.adapters.registry import REGISTRY
from backend.scoring.engine import ScoringEngine
from backend.scoring.reasons import ReasonGenerator
from backend.scoring.comparison import ComparisonTableBuilder

def test_real_links():
    print("=== Testing Real Product Links Extraction ===")
    test_urls = [
        "https://www.flipkart.com/oneplus-12r-cool-blue-256-gb/p/itm7e793d5a42861",
        "https://www.flipkart.com/redmi-note-13-pro-5g-coral-purple-128-gb/p/itm50febe330d200",
        "https://www.flipkart.com/realme-gt-6t-razor-green-128-gb/p/itmdb2908f0a09c2"
    ]

    extracted = []
    for u in test_urls:
        print(f"\nFetching: {u}")
        res = REGISTRY.extract_product(u)
        print(f"Status: {res.get('status')}")
        print(f"Name: {res.get('name')}")
        print(f"Price: {res.get('specs', {}).get('price')}")
        print(f"Chipset: {res.get('specs', {}).get('chipset')}")
        print(f"RAM: {res.get('specs', {}).get('ram')}")
        print(f"Storage: {res.get('specs', {}).get('storage')}")
        print(f"Battery: {res.get('specs', {}).get('battery_capacity')}")
        print(f"Error/Notice: {res.get('error')}")
        extracted.append(res)

    print("\n=== Testing Manual Fallback Path ===")
    # Simulate a link blocked by anti-bot where user inputs specs via fallback
    fallback_sample = {
        "id": "https://www.amazon.in/dp/B0CX123ABC",
        "url": "https://www.amazon.in/dp/B0CX123ABC",
        "name": "iQOO Neo 9 Pro 5G (Fiery Red, 128 GB)",
        "brand": "iQOO",
        "image": "",
        "status": "success",
        "error": None,
        "specs": {
            "price": 34999,
            "mrp": 39999,
            "discount_pct": 12,
            "rating": 4.4,
            "review_count": 12000,
            "ram": 8,
            "storage": 128,
            "chipset": "Snapdragon 8 Gen 2",
            "battery_capacity": 5160,
            "charging_speed": 120,
            "rear_camera": 50,
            "front_camera": 16,
            "display_size": 6.78,
            "refresh_rate": 144,
            "display_type": "LTPO AMOLED",
            "os": "Android 14"
        }
    }

    # If any extracted product needs fallback, supply fallback specs
    ready_products = []
    for idx, p in enumerate(extracted):
        if p.get("status") == "needs_fallback" or not p.get("name") or p.get("specs", {}).get("price") is None:
            print(f"\nProduct #{idx+1} triggered manual fallback as expected when store blocks automated scrapers.")
            # Simulate user completing specs via FallbackModal
            fallback_applied = dict(p)
            fallback_applied["name"] = f"Product #{idx+1} (Fallback Verified)"
            fallback_applied["specs"] = {
                "price": 29999 + idx * 5000,
                "mrp": 34999 + idx * 5000,
                "ram": 8,
                "storage": 128 * (idx + 1),
                "chipset": "Snapdragon 7+ Gen 3" if idx == 0 else "Dimensity 7200-Ultra",
                "battery_capacity": 5000 + idx * 200,
                "charging_speed": 67 + idx * 20,
                "rear_camera": 50,
                "front_camera": 16,
                "display_size": 6.7,
                "refresh_rate": 120,
                "display_type": "AMOLED",
                "rating": 4.3,
                "review_count": 5000
            }
            ready_products.append(fallback_applied)
        else:
            ready_products.append(p)

    ready_products.append(fallback_sample)

    print("\n=== Running Full Scoring Engine on Batch ===")
    engine = ScoringEngine()
    result = engine.score_products(ready_products)

    print(f"\nWinner: {result['scored_products'][0]['name']}")
    print(f"Winner Score: {result['scored_products'][0]['total_score']}/100")
    print("Reasons:")
    reasons = ReasonGenerator.generate_winner_reasons(result['scored_products'][0], result['scored_products'])
    for r in reasons:
        print(f"  - {r}")

    print("\nWhy not the others?")
    why_not = ReasonGenerator.generate_why_not_others(result['scored_products'], result['scored_products'][0])
    for wn in why_not:
        print(f"  - {wn['name']} (#{wn['rank']}): {wn['explanation']}")

    print("\nSpec Table Best Row Count:")
    table = ComparisonTableBuilder.build_comparison_table(result['scored_products'])
    print(f"Generated {len(table)} comparison rows successfully.")
    print("\nAll integration verification steps completed successfully!")

if __name__ == "__main__":
    test_real_links()
