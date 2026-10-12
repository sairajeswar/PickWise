import pytest
import json
from backend.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_categories_endpoint(client):
    res = client.get("/api/categories")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    cat_ids = [c["id"] for c in data["categories"]]
    assert "smartphones" in cat_ids
    assert "laptops" in cat_ids

def test_presets_endpoint(client):
    res = client.get("/api/presets?category=smartphones")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    presets = data["presets"]
    assert "Balanced" in presets
    assert "Gaming" in presets
    assert "Camera" in presets
    assert "Battery" in presets
    assert "Budget" in presets

def test_chipsets_endpoint(client):
    res = client.get("/api/chipsets")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["chipsets"]) >= 40

def test_compare_endpoint_valid_products(client):
    payload = {
        "products": [
            {
                "id": "p1",
                "name": "Phone Alpha",
                "specs": {
                    "price": 29999,
                    "ram": 8,
                    "storage": 128,
                    "chipset": "Snapdragon 8 Gen 2",
                    "battery_capacity": 5000,
                    "charging_speed": 67,
                    "rear_camera": 50,
                    "front_camera": 16,
                    "refresh_rate": 120,
                    "rating": 4.5,
                    "review_count": 8000
                }
            },
            {
                "id": "p2",
                "name": "Phone Beta",
                "specs": {
                    "price": 24999,
                    "ram": 8,
                    "storage": 256,
                    "chipset": "Dimensity 8300",
                    "battery_capacity": 5500,
                    "charging_speed": 45,
                    "rear_camera": 64,
                    "front_camera": 32,
                    "refresh_rate": 120,
                    "rating": 4.3,
                    "review_count": 5000
                }
            }
        ],
        "weights": {
            "price": 30,
            "performance": 20,
            "camera": 15,
            "battery": 15,
            "display": 10,
            "storage": 5,
            "ratings": 5
        }
    }
    res = client.post("/api/compare", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "winner" in data
    assert "ranked_products" in data
    assert len(data["ranked_products"]) == 2
    assert "category_winners" in data
    assert "spec_comparison_table" in data
    assert "why_not_others" in data

def test_compare_endpoint_validation(client):
    # Only 1 product
    res = client.post("/api/compare", json={"products": [{"id": "1", "name": "Solo"}]})
    assert res.status_code == 400
    assert "between 2 and 5" in res.get_json()["error"]
