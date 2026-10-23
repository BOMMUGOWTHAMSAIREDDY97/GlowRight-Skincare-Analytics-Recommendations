"""Automated integration tests for Flask REST API endpoints."""

import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "GlowRight"
    assert "products_count" in data


def test_summary_endpoint(client):
    res = client.get("/api/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert "catalogue" in data
    assert "total_products" in data["catalogue"]
    assert "disclaimer" in data


def test_products_list_and_filter(client):
    # Base list
    res = client.get("/api/products?per_page=5")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["products"]) <= 5
    assert "pagination" in data

    # Filter by category
    res_cat = client.get("/api/products?category=Cleanser")
    assert res_cat.status_code == 200
    cat_data = res_cat.get_json()
    for p in cat_data["products"]:
        assert p["category"] == "Cleanser"

    # Filter by max_price
    res_price = client.get("/api/products?max_price=20")
    assert res_price.status_code == 200
    price_data = res_price.get_json()
    for p in price_data["products"]:
        assert p["price"] <= 20.0


def test_single_product_details(client):
    # Product that exists
    res = client.get("/api/products/GR-001")
    assert res.status_code == 200
    data = res.get_json()
    assert data["product"]["product_id"] == "GR-001"
    assert "reviews" in data

    # Invalid product
    res_invalid = client.get("/api/products/NON-EXISTENT-999")
    assert res_invalid.status_code == 404


def test_recommendation_api(client):
    payload = {
        "query": "soothing hyaluronic acid",
        "preferred_ingredients": ["Hyaluronic Acid"],
        "excluded_ingredients": ["Fragrance"],
        "category": "Serum",
        "max_budget": 35.0,
        "top_k": 3,
    }
    res = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "recommendations" in data
    assert "baseline_popular" in data
    assert "disclaimer" in data
    assert len(data["recommendations"]) <= 3


def test_recommendation_invalid_budget(client):
    payload = {
        "query": "serum",
        "max_budget": -50.0,  # Negative budget
    }
    res = client.post(
        "/api/recommend",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 400


def test_sentiment_prediction_api(client):
    payload = {"review_text": "This oat cream is absolutely wonderful and hydrated my barrier!"}
    res = client.post(
        "/api/sentiment/predict",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["prediction"] in ["positive", "neutral", "negative"]
    assert "confidence" in data
    assert "probabilities" in data

    # Empty payload check
    res_empty = client.post(
        "/api/sentiment/predict",
        data=json.dumps({"review_text": ""}),
        content_type="application/json",
    )
    assert res_empty.status_code == 400


def test_evaluation_endpoint(client):
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.get_json()
    assert "status" in data
