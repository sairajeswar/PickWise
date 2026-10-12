import pytest
from backend.scoring.engine import ScoringEngine
from backend.scoring.reasons import ReasonGenerator
from backend.scoring.comparison import ComparisonTableBuilder
from backend.categories.smartphones import SmartphoneCategory

@pytest.fixture
def sample_phone_a():
    return {
        "id": "phone-a",
        "name": "OnePlus 12R",
        "brand": "OnePlus",
        "url": "https://www.flipkart.com/oneplus-12r",
        "specs": {
            "price": 39999,
            "mrp": 42999,
            "discount_pct": 7,
            "rating": 4.5,
            "review_count": 8500,
            "ram": 16,
            "storage": 256,
            "chipset": "Snapdragon 8 Gen 2",
            "battery_capacity": 5500,
            "charging_speed": 100,
            "rear_camera": 50,
            "front_camera": 16,
            "display_size": 6.78,
            "refresh_rate": 120,
            "display_type": "AMOLED",
            "os": "Android 14"
        }
    }

@pytest.fixture
def sample_phone_b():
    return {
        "id": "phone-b",
        "name": "iQOO Neo 9 Pro",
        "brand": "iQOO",
        "url": "https://www.amazon.in/iqoo-neo-9-pro",
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

@pytest.fixture
def sample_phone_budget():
    return {
        "id": "phone-budget",
        "name": "Redmi 13C 5G",
        "brand": "Redmi",
        "url": "https://www.flipkart.com/redmi-13c-5g",
        "specs": {
            "price": 9999,
            "mrp": 13999,
            "discount_pct": 28,
            "rating": 4.2,
            "review_count": 45000,
            "ram": 4,
            "storage": 128,
            "chipset": "Dimensity 6100+",
            "battery_capacity": 5000,
            "charging_speed": 18,
            "rear_camera": 50,
            "front_camera": 5,
            "display_size": 6.74,
            "refresh_rate": 90,
            "display_type": "IPS LCD",
            "os": "Android 13"
        }
    }

def test_two_products_comparison(sample_phone_a, sample_phone_b):
    engine = ScoringEngine()
    result = engine.score_products([sample_phone_a, sample_phone_b])
    
    assert len(result["scored_products"]) == 2
    assert result["scored_products"][0]["rank"] == 1
    assert result["scored_products"][1]["rank"] == 2
    assert 0 <= result["scored_products"][0]["total_score"] <= 100
    assert 0 <= result["scored_products"][1]["total_score"] <= 100

def test_five_products_comparison(sample_phone_a, sample_phone_b, sample_phone_budget):
    p4 = dict(sample_phone_a)
    p4["id"] = "phone-4"
    p4["name"] = "Realme GT 6T"
    p4["specs"] = dict(sample_phone_a["specs"])
    p4["specs"]["price"] = 30999
    p4["specs"]["chipset"] = "Snapdragon 7+ Gen 3"

    p5 = dict(sample_phone_b)
    p5["id"] = "phone-5"
    p5["name"] = "Motorola Edge 50 Pro"
    p5["specs"] = dict(sample_phone_b["specs"])
    p5["specs"]["price"] = 29999
    p5["specs"]["chipset"] = "Snapdragon 7 Gen 3"

    engine = ScoringEngine()
    result = engine.score_products([sample_phone_a, sample_phone_b, sample_phone_budget, p4, p5])
    
    assert len(result["scored_products"]) == 5
    ranks = [p["rank"] for p in result["scored_products"]]
    assert ranks == [1, 2, 3, 4, 5]

def test_identical_products_ties(sample_phone_a):
    import copy
    p1 = copy.deepcopy(sample_phone_a)
    p1["id"] = "phone-1"
    p2 = copy.deepcopy(sample_phone_a)
    p2["id"] = "phone-2"

    engine = ScoringEngine()
    result = engine.score_products([p1, p2])

    s1 = result["scored_products"][0]["total_score"]
    s2 = result["scored_products"][1]["total_score"]
    # Identical products must have exact identical score
    assert s1 == s2
    assert result["close_call"]["is_close_call"] is True

def test_missing_data_weight_redistribution_and_confidence(sample_phone_a, sample_phone_b):
    import copy
    p_missing = copy.deepcopy(sample_phone_b)
    p_missing["id"] = "phone-missing"
    # Remove multiple key specs
    p_missing["specs"]["charging_speed"] = None
    p_missing["specs"]["front_camera"] = None
    p_missing["specs"]["chipset"] = None
    p_missing["specs"]["refresh_rate"] = None

    engine = ScoringEngine()
    result = engine.score_products([sample_phone_a, p_missing])

    scored_missing = [p for p in result["scored_products"] if p["product_id"] == "phone-missing"][0]
    # Check that missing metrics were detected
    assert len(scored_missing["missing_metrics"]) >= 3
    # Check confidence drop
    assert scored_missing["confidence_pct"] < 80.0
    assert scored_missing["is_low_confidence"] is True
    # Still produces a valid redistributed total score
    assert 0 <= scored_missing["total_score"] <= 100

def test_bayesian_rating_damping():
    # 4.9 rating with only 5 reviews vs 4.4 rating with 25,000 reviews
    r_few = SmartphoneCategory.calculate_bayesian_rating(4.9, 5)
    r_many = SmartphoneCategory.calculate_bayesian_rating(4.4, 25000)

    # With only 5 reviews, Bayesian prior (4.0) pulls the score down toward ~4.04
    # With 25,000 reviews, high confidence maintains the score near ~4.398
    assert r_many > r_few

def test_close_call_detection(sample_phone_a):
    import copy
    p1 = copy.deepcopy(sample_phone_a)
    p1["id"] = "phone-1"
    p2 = copy.deepcopy(sample_phone_a)
    p2["id"] = "phone-2"
    # p1 has 12GB RAM (+5% weight), p2 has 120W charging (+5% weight)
    # This balances out with a small net difference <= 3 points
    p1["specs"]["ram"] = 12
    p1["specs"]["charging_speed"] = 80
    p2["specs"]["ram"] = 8
    p2["specs"]["charging_speed"] = 100

    engine = ScoringEngine()
    result = engine.score_products([p1, p2])

    assert result["close_call"]["is_close_call"] is True
    assert "deciding_factor" in result["close_call"]
    assert "recommendation" in result["close_call"]

def test_reasons_and_why_not_generation(sample_phone_a, sample_phone_b):
    engine = ScoringEngine()
    result = engine.score_products([sample_phone_a, sample_phone_b])
    winner = result["scored_products"][0]

    reasons = ReasonGenerator.generate_winner_reasons(winner, result["scored_products"])
    assert len(reasons) >= 3
    assert all(isinstance(r, str) and len(r) > 10 for r in reasons)

    why_not = ReasonGenerator.generate_why_not_others(result["scored_products"], winner)
    assert len(why_not) == 1
    assert why_not[0]["product_id"] == result["scored_products"][1]["product_id"]
    assert len(why_not[0]["explanation"]) > 10

def test_spec_comparison_table_best_values(sample_phone_a, sample_phone_b):
    engine = ScoringEngine()
    result = engine.score_products([sample_phone_a, sample_phone_b])
    table = ComparisonTableBuilder.build_comparison_table(result["scored_products"])

    assert len(table) > 10
    # Check price row: lower price should be marked as best
    price_row = next(r for r in table if r["key"] == "price")
    best_price_cells = [c for c in price_row["cells"] if c["is_best"]]
    assert len(best_price_cells) == 1
    # 34999 is lower than 39999
    assert best_price_cells[0]["numeric_value"] == 34999

def test_invalid_product_counts(sample_phone_a):
    engine = ScoringEngine()
    with pytest.raises(ValueError, match="at least 2"):
        engine.score_products([sample_phone_a])
    
    with pytest.raises(ValueError, match="at most 5"):
        engine.score_products([sample_phone_a] * 6)
