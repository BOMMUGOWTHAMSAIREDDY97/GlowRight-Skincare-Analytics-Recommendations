"""Comprehensive model evaluation module for GlowRight.
Evaluates both Supervised Sentiment Classification (Accuracy, Precision, Recall, F1, CM)
and Content-based Recommendations (Precision@K, Recall@K, NDCG@K, Catalogue Coverage).
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

from src.config import (
    EVALUATION_METRICS_PATH,
    CLEAN_PRODUCTS_PATH,
    CLEAN_REVIEWS_PATH,
)
from src.recommender import ContentRecommender
from src.sentiment import SentimentClassifierPipeline

logger = logging.getLogger(__name__)


# Benchmark validation suite for recommender evaluation
RECOMMENDER_BENCHMARK_SCENARIOS = [
    {
        "scenario_id": "BENCH-01",
        "description": "Hydrating hyaluronic serum for moisture barrier",
        "query": "hydrating hyaluronic acid serum plumping",
        "category": "Serum",
        "preferred_ingredients": ["Hyaluronic Acid", "Sodium Hyaluronate"],
        "excluded_ingredients": ["Fragrance"],
        "max_budget": 35.0,
        "k": 5,
    },
    {
        "scenario_id": "BENCH-02",
        "description": "Blemish clarifying cleanser with salicylic acid BHA",
        "query": "salicylic acid acne clarifying wash pores",
        "category": "Cleanser",
        "preferred_ingredients": ["Salicylic Acid", "Zinc PCA"],
        "excluded_ingredients": [],
        "max_budget": 25.0,
        "k": 5,
    },
    {
        "scenario_id": "BENCH-03",
        "description": "Soothing barrier repair cica moisturizer for redness",
        "query": "centella cica soothing redness barrier cream",
        "category": "Moisturizer",
        "preferred_ingredients": ["Centella Asiatica", "Ceramide NP"],
        "excluded_ingredients": ["Fragrance"],
        "max_budget": 30.0,
        "k": 5,
    },
    {
        "scenario_id": "BENCH-04",
        "description": "Anti-aging retinol and peptide renewal serum",
        "query": "retinol peptides fine lines wrinkles",
        "category": "Serum",
        "preferred_ingredients": ["Retinol", "Peptide"],
        "excluded_ingredients": [],
        "max_budget": 50.0,
        "k": 5,
    },
    {
        "scenario_id": "BENCH-05",
        "description": "Mineral physical sunscreen for reactive sensitive skin",
        "query": "mineral zinc oxide sunscreen physical",
        "category": "Sunscreen",
        "preferred_ingredients": ["Zinc Oxide"],
        "excluded_ingredients": [],
        "max_budget": 35.0,
        "k": 5,
    },
    {
        "scenario_id": "BENCH-06",
        "description": "Gentle daily hydrating toner for sensitive skin",
        "query": "milky calming hydrating toner after cleansing",
        "category": "Toner",
        "preferred_ingredients": ["Ceramide", "Centella Asiatica"],
        "excluded_ingredients": ["Alcohol Denat."],
        "max_budget": 25.0,
        "k": 5,
    },
]


def is_product_ground_truth_relevant(product: pd.Series, scenario: Dict[str, Any]) -> bool:
    """Ground-truth relevance check based on strict domain heuristics."""
    # 1. Category constraint
    if scenario.get("category"):
        if product["category"].lower() != scenario["category"].lower():
            return False

    # 2. Budget constraint
    if scenario.get("max_budget") and product["price"] > scenario["max_budget"]:
        return False

    # 3. Excluded ingredients
    ing_lower = str(product.get("ingredients_normalized", "")).lower()
    for excl in scenario.get("excluded_ingredients", []):
        if excl.lower() in ing_lower:
            return False

    # 4. Relevant if it contains at least one preferred ingredient or relevant keyword
    for pref in scenario.get("preferred_ingredients", []):
        if pref.lower() in ing_lower:
            return True

    text = (str(product["product_name"]) + " " + str(product["description"])).lower()
    query_tokens = [w for w in scenario["query"].lower().split() if len(w) > 3]
    overlap = sum(1 for t in query_tokens if t in text)
    return overlap >= 2


def evaluate_recommender(
    recommender: ContentRecommender,
    products_df: pd.DataFrame,
    scenarios: List[Dict[str, Any]] = RECOMMENDER_BENCHMARK_SCENARIOS,
    k: int = 5,
) -> Dict[str, Any]:
    """Evaluates recommendation quality across benchmark scenarios."""
    precision_scores = []
    recall_scores = []
    ndcg_scores = []
    all_recommended_ids = set()

    scenario_breakdowns = []

    for sc in scenarios:
        top_k = sc.get("k", k)
        # Determine total ground-truth relevant items in entire catalogue
        gt_relevant_df = products_df[
            products_df.apply(lambda p: is_product_ground_truth_relevant(p, sc), axis=1)
        ]
        total_relevant = len(gt_relevant_df)

        # Run recommender
        rec_res = recommender.recommend(
            query=sc["query"],
            preferred_ingredients=sc.get("preferred_ingredients", []),
            excluded_ingredients=sc.get("excluded_ingredients", []),
            category=sc.get("category"),
            max_budget=sc.get("max_budget"),
            top_k=top_k,
        )
        recommended_items = rec_res["recommendations"]

        hits = 0
        dcg = 0.0

        for rank, item in enumerate(recommended_items, start=1):
            all_recommended_ids.add(item["product_id"])
            prod_row = products_df[products_df["product_id"] == item["product_id"]].iloc[0]
            is_rel = 1 if is_product_ground_truth_relevant(prod_row, sc) else 0
            hits += is_rel
            if is_rel:
                dcg += 1.0 / math.log2(rank + 1)

        # Precision@K
        p_at_k = hits / top_k if top_k > 0 else 0.0
        precision_scores.append(p_at_k)

        # Recall@K
        r_at_k = hits / total_relevant if total_relevant > 0 else 1.0
        recall_scores.append(r_at_k)

        # Ideal DCG@K
        idcg = sum(1.0 / math.log2(r + 1) for r in range(1, min(total_relevant, top_k) + 1))
        ndcg_at_k = (dcg / idcg) if idcg > 0 else 0.0
        ndcg_scores.append(ndcg_at_k)

        scenario_breakdowns.append({
            "scenario_id": sc["scenario_id"],
            "description": sc["description"],
            "category": sc.get("category"),
            "total_ground_truth_relevant": total_relevant,
            "retrieved_count": len(recommended_items),
            "hits_at_k": hits,
            "precision_at_k": round(p_at_k, 4),
            "recall_at_k": round(r_at_k, 4),
            "ndcg_at_k": round(ndcg_at_k, 4),
        })

    # Catalogue Coverage
    total_catalogue = len(products_df)
    coverage_pct = (len(all_recommended_ids) / total_catalogue) * 100 if total_catalogue > 0 else 0.0

    return {
        "k_value": k,
        "scenarios_evaluated": len(scenarios),
        "mean_precision_at_k": round(float(np.mean(precision_scores)), 4),
        "mean_recall_at_k": round(float(np.mean(recall_scores)), 4),
        "mean_ndcg_at_k": round(float(np.mean(ndcg_scores)), 4),
        "catalogue_coverage_percentage": round(coverage_pct, 2),
        "unique_products_recommended": len(all_recommended_ids),
        "total_catalogue_size": total_catalogue,
        "scenario_details": scenario_breakdowns,
        "metric_explanations": {
            "Precision@K": "Fraction of the top-K recommended products that strictly meet the user's category, budget, and active ingredient criteria.",
            "Recall@K": "Proportion of all valid candidate products in the catalogue successfully surfaced in the top-K recommendations.",
            "NDCG@K": "Normalized Discounted Cumulative Gain penalizing relevant products placed lower in the ranking.",
            "Catalogue Coverage": "Percentage of unique catalogue items surfaced across varied benchmark user profiles, measuring recommendation diversity.",
        },
        "limitations": "Relevance is assessed against synthetic benchmark scenarios. Live customer A/B testing and click-through tracking are required for production validation.",
    }


def run_full_evaluation(
    products_path: Path = CLEAN_PRODUCTS_PATH,
    reviews_path: Path = CLEAN_REVIEWS_PATH,
    save_path: Path = EVALUATION_METRICS_PATH,
) -> Dict[str, Any]:
    """Runs end-to-end evaluation for both Sentiment and Recommender pipelines."""
    logger.info("Executing comprehensive model evaluation...")

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    # 1. Sentiment Pipeline Evaluation
    sentiment_pipeline = SentimentClassifierPipeline()
    sentiment_metrics = sentiment_pipeline.train_and_evaluate(reviews_df)
    sentiment_pipeline.save()

    # 2. Recommender Engine Evaluation
    recommender = ContentRecommender()
    recommender.fit(products_df)
    recommender.save()
    recommender_metrics = evaluate_recommender(recommender, products_df, k=5)

    full_evaluation = {
        "status": "evaluated",
        "evaluation_timestamp": "2026-03-20T10:00:00Z",
        "sentiment_classification": sentiment_metrics,
        "content_recommender": recommender_metrics,
    }

    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(full_evaluation, f, indent=2)

    logger.info(f"Evaluation report persisted to {save_path}")
    return full_evaluation
