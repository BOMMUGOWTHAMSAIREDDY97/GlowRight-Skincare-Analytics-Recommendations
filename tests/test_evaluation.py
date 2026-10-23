"""Automated unit tests for Evaluation and Sentiment Pipeline."""

import pytest
import pandas as pd
from src.sentiment import SentimentClassifierPipeline
from src.evaluation import evaluate_recommender
from src.recommender import ContentRecommender


@pytest.fixture
def mock_reviews():
    # 30 reviews with balanced classes for testing
    data = []
    for i in range(10):
        data.append({
            "review_id": f"R-POS-{i}",
            "product_id": "P-01",
            "rating": 5.0,
            "review_text": f"Wonderful, calming, soothing holy grail product {i}!",
            "sentiment": "positive",
        })
        data.append({
            "review_id": f"R-NEU-{i}",
            "product_id": "P-01",
            "rating": 3.0,
            "review_text": f"Average cleanser, nothing revolutionary or special {i}.",
            "sentiment": "neutral",
        })
        data.append({
            "review_id": f"R-NEG-{i}",
            "product_id": "P-01",
            "rating": 1.0,
            "review_text": f"Terrible severe breakouts, burning, and clogged pores {i}!",
            "sentiment": "negative",
        })
    return pd.DataFrame(data)


def test_sentiment_pipeline_training_and_metrics(mock_reviews):
    pipeline = SentimentClassifierPipeline()
    results = pipeline.train_and_evaluate(mock_reviews, test_size=0.3, random_state=42)

    assert pipeline.is_trained
    assert "metrics" in results
    assert "accuracy" in results["metrics"]
    assert "macro_f1" in results["metrics"]
    assert 0.0 <= results["metrics"]["accuracy"] <= 1.0
    assert 0.0 <= results["metrics"]["macro_f1"] <= 1.0

    # Ensure confusion matrix is present
    cm = results["confusion_matrix"]
    assert len(cm["labels"]) == 3
    assert len(cm["matrix"]) == 3

    # Prediction test
    pred = pipeline.predict("I really love this amazing gentle serum!")
    assert pred["prediction"] in ["positive", "neutral", "negative"]
    assert "confidence" in pred
    assert "probabilities" in pred


def test_sentiment_pipeline_empty_input(mock_reviews):
    pipeline = SentimentClassifierPipeline()
    pipeline.train_and_evaluate(mock_reviews, test_size=0.3, random_state=42)

    # Empty string should return neutral fallback without crashing
    pred = pipeline.predict("")
    assert pred["prediction"] == "neutral"


def test_recommender_evaluation_metrics():
    products = pd.DataFrame([
        {
            "product_id": "P-01",
            "product_name": "Hydrating Hyaluronic Plumping Serum",
            "brand": "BrandA",
            "category": "Serum",
            "price": 25.0,
            "rating": 4.8,
            "review_count": 200,
            "ingredients_normalized": "Aqua, Hyaluronic Acid, Glycerin",
            "description": "Multi-molecular hyaluronic acid plumping moisture drops.",
            "is_demo": True,
        },
        {
            "product_id": "P-02",
            "product_name": "Blemish Clarifying Cleanser",
            "brand": "BrandB",
            "category": "Cleanser",
            "price": 18.0,
            "rating": 4.5,
            "review_count": 150,
            "ingredients_normalized": "Aqua, Salicylic Acid, Zinc PCA",
            "description": "Pore clarifying wash with salicylic acid for acne.",
            "is_demo": True,
        },
    ])

    rec = ContentRecommender().fit(products)
    benchmark_scenarios = [
        {
            "scenario_id": "TEST-01",
            "description": "Hyaluronic acid serum",
            "query": "hyaluronic acid hydrating serum",
            "category": "Serum",
            "preferred_ingredients": ["Hyaluronic Acid"],
            "excluded_ingredients": [],
            "max_budget": 30.0,
            "k": 2,
        }
    ]

    metrics = evaluate_recommender(rec, products, scenarios=benchmark_scenarios, k=2)

    assert "mean_precision_at_k" in metrics
    assert "mean_recall_at_k" in metrics
    assert "mean_ndcg_at_k" in metrics
    assert "catalogue_coverage_percentage" in metrics
    assert 0.0 <= metrics["mean_precision_at_k"] <= 1.0
    assert 0.0 <= metrics["mean_ndcg_at_k"] <= 1.0
