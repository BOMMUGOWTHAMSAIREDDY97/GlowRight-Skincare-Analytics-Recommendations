"""Automated unit tests for Content-Based Recommender."""

import pytest
import pandas as pd
from src.recommender import ContentRecommender


@pytest.fixture
def sample_products():
    return pd.DataFrame([
        {
            "product_id": "P-01",
            "product_name": "Hydrating Niacinamide Serum",
            "brand": "BrandA",
            "category": "Serum",
            "price": 20.0,
            "rating": 4.8,
            "review_count": 300,
            "ingredients_normalized": "Aqua, Niacinamide, Glycerin, Sodium Hyaluronate",
            "description": "Hydrating serum for redness and pore reduction.",
            "is_demo": True,
        },
        {
            "product_id": "P-02",
            "product_name": "Fragrance Rich Day Cream",
            "brand": "BrandB",
            "category": "Moisturizer",
            "price": 50.0,
            "rating": 4.2,
            "review_count": 100,
            "ingredients_normalized": "Aqua, Shea Butter, Fragrance (Parfum), Glycerin",
            "description": "Heavy day cream with perfumed floral scent.",
            "is_demo": True,
        },
        {
            "product_id": "P-03",
            "product_name": "Gentle Oat Cleanser",
            "brand": "BrandC",
            "category": "Cleanser",
            "price": 15.0,
            "rating": 4.9,
            "review_count": 450,
            "ingredients_normalized": "Aqua, Oat Kernel Extract, Glycerin, Allantoin",
            "description": "Soothing cream wash for delicate and sensitive skin.",
            "is_demo": True,
        },
        {
            "product_id": "P-04",
            "product_name": "Salicylic Acid BHA Gel",
            "brand": "BrandA",
            "category": "Serum",
            "price": 28.0,
            "rating": 4.4,
            "review_count": 180,
            "ingredients_normalized": "Aqua, Salicylic Acid 2%, Tea Tree Oil",
            "description": "Clarifying gel targeting congested blackheads.",
            "is_demo": True,
        },
    ])


@pytest.fixture
def recommender(sample_products):
    rec = ContentRecommender()
    rec.fit(sample_products)
    return rec


def test_recommender_hard_exclusion_filter(recommender):
    # P-02 contains Fragrance
    results = recommender.recommend(
        query="day cream moisturizer",
        excluded_ingredients=["Fragrance"],
        top_k=5,
    )
    product_ids = [p["product_id"] for p in results["recommendations"]]
    assert "P-02" not in product_ids


def test_recommender_budget_constraint(recommender):
    results = recommender.recommend(
        query="serum",
        max_budget=22.0,
        top_k=5,
    )
    for p in results["recommendations"]:
        assert p["price"] <= 22.0
    # P-04 price is 28.0, so should be filtered out
    product_ids = [p["product_id"] for p in results["recommendations"]]
    assert "P-04" not in product_ids


def test_recommender_category_filter(recommender):
    results = recommender.recommend(
        query="gentle hydration",
        category="Cleanser",
        top_k=5,
    )
    for p in results["recommendations"]:
        assert p["category"] == "Cleanser"
    assert len(results["recommendations"]) == 1
    assert results["recommendations"][0]["product_id"] == "P-03"


def test_recommender_preferred_ingredients_ranking(recommender):
    results = recommender.recommend(
        query="hydrating serum",
        preferred_ingredients=["Niacinamide"],
        top_k=2,
    )
    top_match = results["recommendations"][0]
    assert top_match["product_id"] == "P-01"
    # Match reasons should include requested ingredient
    reasons_str = " ".join(top_match["match_reasons"])
    assert "Niacinamide" in reasons_str


def test_recommender_empty_query_fallback(recommender):
    results = recommender.recommend(
        query="",
        preferred_ingredients=[],
        top_k=2,
    )
    # Should fall back to popularity baseline gracefully
    assert len(results["recommendations"]) > 0
    assert "baseline_popular" in results
    assert "No specific query" in results["metadata"]["message"]


def test_recommender_no_matching_products(recommender):
    results = recommender.recommend(
        query="moisturizer",
        category="Moisturizer",
        max_budget=10.0,  # No moisturizer under $10 in sample
    )
    assert len(results["recommendations"]) == 0
    assert results["metadata"]["candidates_after_filters"] == 0
