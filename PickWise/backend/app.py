"""
Flask Application for PickWise API.
Provides product extraction, caching, deterministic comparison,
and transparent scoring endpoints.
"""

import time
from collections import defaultdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.adapters.registry import REGISTRY
from backend.categories import get_category, CATEGORIES
from backend.categories.smartphones import CHIPSET_DB
from backend.scoring.engine import ScoringEngine
from backend.scoring.reasons import ReasonGenerator
from backend.scoring.comparison import ComparisonTableBuilder

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Rate limiter: 60 requests per minute per IP
RATE_LIMIT_STORE = defaultdict(list)
RATE_LIMIT_MAX = 60
RATE_LIMIT_WINDOW = 60  # seconds

@app.before_request
def check_rate_limit():
    if request.path.startswith("/api/"):
        client_ip = request.remote_addr or "127.0.0.1"
        now = time.time()
        # Clean older requests
        RATE_LIMIT_STORE[client_ip] = [t for t in RATE_LIMIT_STORE[client_ip] if now - t < RATE_LIMIT_WINDOW]
        if len(RATE_LIMIT_STORE[client_ip]) >= RATE_LIMIT_MAX:
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded. Please wait a moment before trying again."
            }), 429
        RATE_LIMIT_STORE[client_ip].append(now)

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PickWise API",
        "version": "1.0.0"
    })

@app.route("/api/categories", methods=["GET"])
def list_categories():
    data = []
    for cat_id, cat_cls in CATEGORIES.items():
        data.append({
            "id": cat_id,
            "name": cat_cls.name,
            "groups": cat_cls.get_groups(),
            "default_weights": cat_cls.get_default_weights(),
            "presets": cat_cls.get_presets()
        })
    return jsonify({"success": True, "categories": data})

@app.route("/api/presets", methods=["GET"])
def get_presets():
    cat_id = request.args.get("category", "smartphones")
    cat_cls = get_category(cat_id)
    return jsonify({
        "success": True,
        "category": cat_id,
        "presets": cat_cls.get_presets(),
        "default_weights": cat_cls.get_default_weights(),
        "groups": cat_cls.get_groups()
    })

@app.route("/api/chipsets", methods=["GET"])
def get_chipsets():
    chipset_list = []
    for k, v in CHIPSET_DB.items():
        chipset_list.append({
            "name": k.title(),
            "score": v["score"],
            "tier": v["tier"],
            "cores": v["cores"]
        })
    chipset_list.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"success": True, "chipsets": chipset_list})

@app.route("/api/extract", methods=["POST"])
def extract_urls():
    """
    Extracts products from provided URLs.
    Validates min 2, max 5, duplicates, and returns per-product results.
    """
    payload = request.get_json(silent=True) or {}
    urls = payload.get("urls", [])
    force_refresh = bool(payload.get("force_refresh", False))

    valid, err_msg, cleaned_urls = REGISTRY.validate_urls(urls)
    if not valid:
        return jsonify({"success": False, "error": err_msg}), 400

    extracted_products = []
    any_needs_fallback = False

    for u in cleaned_urls:
        product_data = REGISTRY.extract_product(u, force_refresh=force_refresh)
        if product_data.get("status") == "needs_fallback":
            any_needs_fallback = True
        extracted_products.append(product_data)

    return jsonify({
        "success": True,
        "products": extracted_products,
        "has_fallback_needed": any_needs_fallback
    })

@app.route("/api/compare", methods=["POST"])
def compare_products():
    """
    Compares 2 to 5 products with user-specified or preset weights.
    Accepts either pre-extracted products OR list of urls.
    """
    payload = request.get_json(silent=True) or {}
    products = payload.get("products")
    urls = payload.get("urls")
    weights = payload.get("weights")
    category_id = payload.get("category", "smartphones")

    # If urls are passed without products, extract them first
    if not products:
        if not urls:
            return jsonify({"success": False, "error": "Either 'products' or 'urls' must be provided."}), 400
        
        valid, err_msg, cleaned_urls = REGISTRY.validate_urls(urls)
        if not valid:
            return jsonify({"success": False, "error": err_msg}), 400
        
        products = REGISTRY.extract_batch(cleaned_urls)

    if len(products) < 2 or len(products) > 5:
        return jsonify({"success": False, "error": "Comparison requires between 2 and 5 products."}), 400

    try:
        category_cls = get_category(category_id)
        engine = ScoringEngine(category=category_cls)
        
        # Calculate deterministic scores
        scoring_result = engine.score_products(products, user_group_weights=weights)
        scored_products = scoring_result["scored_products"]

        winner = scored_products[0]
        winner_reasons = ReasonGenerator.generate_winner_reasons(winner, scored_products)
        why_not_others = ReasonGenerator.generate_why_not_others(scored_products, winner)
        spec_table = ComparisonTableBuilder.build_comparison_table(scored_products)

        return jsonify({
            "success": True,
            "category": category_id,
            "winner": {
                "product_id": winner["product_id"],
                "name": winner["name"],
                "brand": winner["brand"],
                "image": winner["image"],
                "total_score": winner["total_score"],
                "reasons": winner_reasons,
                "confidence_pct": winner["confidence_pct"],
                "is_low_confidence": winner["is_low_confidence"]
            },
            "close_call": scoring_result["close_call"],
            "ranked_products": scored_products,
            "category_winners": scoring_result["category_winners"],
            "spec_comparison_table": spec_table,
            "why_not_others": why_not_others,
            "applied_weights": scoring_result["group_weights"]
        })

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal evaluation error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
