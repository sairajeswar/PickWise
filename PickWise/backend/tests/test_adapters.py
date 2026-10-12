import pytest
from backend.adapters.registry import AdapterRegistry
from backend.adapters.flipkart import FlipkartAdapter
from backend.adapters.amazon import AmazonAdapter

SAMPLE_FLIPKART_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "OnePlus 12R (Cool Blue, 256 GB)",
        "image": "https://rukminim2.flixcart.com/image/oneplus.jpg",
        "brand": {"@type": "Brand", "name": "OnePlus"},
        "offers": {
            "@type": "Offer",
            "price": "39999",
            "priceCurrency": "INR"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.5",
            "reviewCount": "8500"
        }
    }
    </script>
</head>
<body>
    <h1 class="VU-ZEz">OnePlus 12R (Cool Blue, 256 GB)</h1>
    <div class="Nx9bqj CxhGGd">₹39,999</div>
    <div class="yRaY8j A6+L6v">₹42,999</div>
    <div class="XQDdHH">4.5 ★</div>
    <div class="_241R88">
        <ul>
            <li class="_21AqiJ">16 GB RAM | 256 GB ROM</li>
            <li class="_21AqiJ">17.22 cm (6.78 inch) Full HD+ Display</li>
            <li class="_21AqiJ">50MP + 8MP | 16MP Front Camera</li>
            <li class="_21AqiJ">5500 mAh Battery</li>
            <li class="_21AqiJ">Snapdragon 8 Gen 2 Processor</li>
            <li class="_21AqiJ">100W SUPERVOOC Charge</li>
            <li class="_21AqiJ">120 Hz AMOLED Display</li>
        </ul>
    </div>
</body>
</html>
"""

SAMPLE_AMAZON_HTML = """
<!DOCTYPE html>
<html>
<body>
    <span id="productTitle">iQOO Neo 9 Pro 5G (Fiery Red, 8GB RAM, 128GB Storage)</span>
    <span class="a-price"><span class="a-offscreen">₹34,999</span></span>
    <span class="a-price a-text-price"><span class="a-offscreen">₹39,999</span></span>
    <div id="averageCustomerReviews"><span class="a-icon-alt">4.4 out of 5 stars</span></div>
    <span id="acrCustomerReviewText">12,430 ratings</span>
    <div id="feature-bullets">
        <ul>
            <li><span>Snapdragon 8 Gen 2 Mobile Platform</span></li>
            <li><span>120W FlashCharge with 5160 mAh Battery</span></li>
            <li><span>50MP Sony IMX920 Night Vision Camera</span></li>
            <li><span>144 Hz LTPO AMOLED Display</span></li>
        </ul>
    </div>
</body>
</html>
"""

def test_flipkart_adapter_parsing():
    adapter = FlipkartAdapter()
    data = adapter.parse("https://www.flipkart.com/oneplus-12r/p/itm123", SAMPLE_FLIPKART_HTML)

    assert data["status"] == "success"
    assert "OnePlus 12R" in data["name"]
    assert data["specs"]["price"] == 39999
    assert data["specs"]["mrp"] == 42999
    assert data["specs"]["discount_pct"] > 0
    assert data["specs"]["ram"] == 16
    assert data["specs"]["storage"] == 256
    assert data["specs"]["battery_capacity"] == 5500
    assert data["specs"]["charging_speed"] == 100
    assert data["specs"]["rear_camera"] == 50
    assert data["specs"]["front_camera"] == 16
    assert data["specs"]["refresh_rate"] == 120
    assert data["specs"]["display_type"] == "AMOLED"

def test_amazon_adapter_parsing():
    adapter = AmazonAdapter()
    data = adapter.parse("https://www.amazon.in/dp/B0CX123", SAMPLE_AMAZON_HTML)

    assert data["status"] == "success"
    assert "iQOO Neo 9 Pro" in data["name"]
    assert data["specs"]["price"] == 34999
    assert data["specs"]["mrp"] == 39999
    assert data["specs"]["ram"] == 8
    assert data["specs"]["storage"] == 128
    assert data["specs"]["battery_capacity"] == 5160
    assert data["specs"]["charging_speed"] == 120
    assert data["specs"]["rear_camera"] == 50
    assert data["specs"]["refresh_rate"] == 144
    assert data["specs"]["rating"] == 4.4
    assert data["specs"]["review_count"] == 12430

def test_registry_url_validation():
    registry = AdapterRegistry()

    # Fewer than 2 links
    valid, err, _ = registry.validate_urls(["https://www.flipkart.com/test"])
    assert valid is False
    assert "at least 2" in err

    # More than 5 links
    valid, err, _ = registry.validate_urls([f"https://www.flipkart.com/item-{i}" for i in range(6)])
    assert valid is False
    assert "up to 5" in err

    # Unsupported domain
    valid, err, _ = registry.validate_urls(["https://www.flipkart.com/item1", "https://www.walmart.com/item2"])
    assert valid is False
    assert "unsupported store" in err.lower()

    # Duplicate URLs
    valid, err, _ = registry.validate_urls([
        "https://www.flipkart.com/oneplus-12r/p/itm123?pid=123",
        "https://www.flipkart.com/oneplus-12r/p/itm123?source=share"
    ])
    assert valid is False
    assert "duplicate" in err.lower()

def test_fallback_when_html_empty():
    adapter = FlipkartAdapter()
    data = adapter.parse("https://www.flipkart.com/blocked", None)

    assert data["status"] == "needs_fallback"
    assert data["error"] is not None
