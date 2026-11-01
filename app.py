"""Flask REST API and web server for GlowRight.
Serves full-stack skincare product catalogue, content-based recommendations,
review analytics, and machine learning sentiment classification.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import pandas as pd

from src.config import (
    BASE_DIR,
    CLEAN_PRODUCTS_PATH,
    CLEAN_REVIEWS_PATH,
    DATA_SUMMARY_PATH,
    EVALUATION_METRICS_PATH,
    SENTIMENT_MODEL_PATH,
    SENTIMENT_VEC_PATH,
    RECOMMENDER_MODEL_PATH,
    STATIC_DIR,
    WEB_DIR,
    SAFETY_DISCLAIMER,
    DEMO_DATA_NOTICE,
    VALID_CATEGORIES,
    VALID_SENTIMENTS,
    DEFAULT_TOP_K,
    MAX_TOP_K,
)
from src.recommender import ContentRecommender
from src.sentiment import SentimentClassifierPipeline
from src.reporting import get_review_analytics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app")

app = Flask(
    __name__,
    template_folder=str(WEB_DIR / "templates"),
    static_folder=str(STATIC_DIR),
)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
CORS(app)

# Global in-memory cache for models and datasets
APP_STATE: Dict[str, Any] = {
    "products_df": None,
    "reviews_df": None,
    "recommender": None,
    "sentiment_pipeline": None,
    "evaluation_metrics": None,
    "data_summary": None,
    "initialized": False,
}


def load_application_state():
    """Initializes and caches models and data at startup."""
    try:
        # 1. Load Data
        if CLEAN_PRODUCTS_PATH.exists():
            APP_STATE["products_df"] = pd.read_csv(CLEAN_PRODUCTS_PATH)
        else:
            logger.warning("Cleaned products not found. Run run_pipeline.py first.")

        if CLEAN_REVIEWS_PATH.exists():
            APP_STATE["reviews_df"] = pd.read_csv(CLEAN_REVIEWS_PATH)
        else:
            logger.warning("Cleaned reviews not found. Run run_pipeline.py first.")

        # 2. Load Recommender
        recommender_loaded = False
        if RECOMMENDER_MODEL_PATH.exists():
            try:
                APP_STATE["recommender"] = ContentRecommender.load(RECOMMENDER_MODEL_PATH)
                recommender_loaded = True
            except Exception as rec_err:
                logger.warning(f"Failed to load pickled recommender ({rec_err}), falling back to in-memory fit.")
        if not recommender_loaded and APP_STATE["products_df"] is not None:
            APP_STATE["recommender"] = ContentRecommender().fit(APP_STATE["products_df"])

        # 3. Load Sentiment Pipeline
        sentiment_loaded = False
        if SENTIMENT_MODEL_PATH.exists() and SENTIMENT_VEC_PATH.exists():
            try:
                APP_STATE["sentiment_pipeline"] = SentimentClassifierPipeline.load(
                    SENTIMENT_MODEL_PATH, SENTIMENT_VEC_PATH
                )
                sentiment_loaded = True
            except Exception as sent_err:
                logger.warning(f"Failed to load pickled sentiment models ({sent_err}), falling back to in-memory fit.")
        if not sentiment_loaded and APP_STATE["reviews_df"] is not None:
            pipeline = SentimentClassifierPipeline()
            pipeline.train_and_evaluate(APP_STATE["reviews_df"])
            APP_STATE["sentiment_pipeline"] = pipeline

        # 4. Load Evaluation Metrics
        if EVALUATION_METRICS_PATH.exists():
            with open(EVALUATION_METRICS_PATH, "r", encoding="utf-8") as f:
                APP_STATE["evaluation_metrics"] = json.load(f)

        # 5. Load Data Summary
        if DATA_SUMMARY_PATH.exists():
            with open(DATA_SUMMARY_PATH, "r", encoding="utf-8") as f:
                APP_STATE["data_summary"] = json.load(f)

        APP_STATE["initialized"] = True
        logger.info("Application state initialized successfully.")

    except Exception as e:
        logger.exception(f"Error initializing application state: {e}")
        APP_STATE["initialized"] = False


# Initial state loading
load_application_state()


# ---------------------------------------------------------------------------
# Frontend Views
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Renders the main single-page application dashboard."""
    return render_template(
        "index.html",
        safety_disclaimer=SAFETY_DISCLAIMER,
        demo_notice=DEMO_DATA_NOTICE,
    )


# ---------------------------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------------------------
@app.route("/health", methods=["GET"])
def health_check():
    """Service health inspection."""
    return jsonify({
        "status": "healthy",
        "app_name": "GlowRight",
        "version": "1.0.0",
        "initialized": APP_STATE["initialized"],
        "products_count": len(APP_STATE["products_df"]) if APP_STATE["products_df"] is not None else 0,
        "reviews_count": len(APP_STATE["reviews_df"]) if APP_STATE["reviews_df"] is not None else 0,
        "models_ready": APP_STATE["recommender"] is not None and APP_STATE["sentiment_pipeline"] is not None,
    }), 200


@app.route("/api/summary", methods=["GET"])
def get_summary():
    """Returns overall catalogue metrics and data pipeline summary."""
    if APP_STATE["products_df"] is None or APP_STATE["reviews_df"] is None:
        return jsonify({"error": "Data not initialized. Run pipeline first."}), 503

    p_df = APP_STATE["products_df"]
    r_df = APP_STATE["reviews_df"]

    summary = {
        "catalogue": {
            "total_products": len(p_df),
            "total_reviews": len(r_df),
            "average_price": round(float(p_df["price"].mean()), 2),
            "median_price": round(float(p_df["price"].median()), 2),
            "price_range": [float(p_df["price"].min()), float(p_df["price"].max())],
            "average_rating": round(float(p_df["rating"].mean()), 2),
            "total_brands": int(p_df["brand"].nunique()),
            "categories": p_df["category"].value_counts().to_dict(),
        },
        "reviews": {
            "average_rating": round(float(r_df["rating"].mean()), 2),
            "sentiment_distribution": r_df["sentiment"].value_counts().to_dict(),
        },
        "provenance": {
            "dataset_type": "Synthetic Benchmark Demonstration Data",
            "is_demo": True,
            "notice": DEMO_DATA_NOTICE,
        },
        "disclaimer": SAFETY_DISCLAIMER,
    }
    return jsonify(summary), 200


@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Returns available categories with counts."""
    if APP_STATE["products_df"] is None:
        return jsonify({"error": "Products data unavailable."}), 503
    counts = APP_STATE["products_df"]["category"].value_counts().to_dict()
    return jsonify({
        "categories": [{"name": k, "count": v} for k, v in counts.items()],
        "valid_categories": VALID_CATEGORIES,
    }), 200


@app.route("/api/products", methods=["GET"])
def get_products():
    """Returns filtered, searched, sorted, and paginated product items."""
    if APP_STATE["products_df"] is None:
        return jsonify({"error": "Products data unavailable."}), 503

    df = APP_STATE["products_df"].copy()

    # Query params
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    max_price = request.args.get("max_price", type=float)
    sort_by = request.args.get("sort_by", "rating").lower()
    sort_dir = request.args.get("sort_dir", "desc").lower()
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", 12, type=int)))

    # Filter: Category
    if category and category.lower() != "all":
        df = df[df["category"].str.lower() == category.lower()]

    # Filter: Max Price
    if max_price is not None and max_price > 0:
        df = df[df["price"] <= max_price]

    # Filter: Search (Name, Brand, Ingredients, Description)
    if search:
        q = search.lower()
        search_mask = (
            df["product_name"].str.lower().str.contains(q, regex=False) |
            df["brand"].str.lower().str.contains(q, regex=False) |
            df["ingredients"].str.lower().str.contains(q, regex=False) |
            df["description"].str.lower().str.contains(q, regex=False)
        )
        df = df[search_mask]

    # Sort
    sort_column_map = {
        "price": "price",
        "rating": "rating",
        "reviews": "review_count",
        "name": "product_name",
    }
    col = sort_column_map.get(sort_by, "rating")
    ascending = (sort_dir == "asc")
    df = df.sort_values(by=col, ascending=ascending)

    total_records = len(df)
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page
    paginated_items = df.iloc[start_idx : start_idx + per_page].to_dict(orient="records")

    return jsonify({
        "products": paginated_items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_records": total_records,
            "total_pages": total_pages,
        },
        "filters_applied": {
            "search": search,
            "category": category,
            "max_price": max_price,
            "sort_by": sort_by,
            "sort_dir": sort_dir,
        },
    }), 200


@app.route("/api/products/<product_id>", methods=["GET"])
def get_product_details(product_id: str):
    """Returns single product details and linked reviews."""
    if APP_STATE["products_df"] is None:
        return jsonify({"error": "Products data unavailable."}), 503

    p_df = APP_STATE["products_df"]
    match = p_df[p_df["product_id"].str.upper() == product_id.strip().upper()]
    if match.empty:
        return jsonify({"error": f"Product '{product_id}' not found."}), 404

    product_data = match.iloc[0].to_dict()

    # Fetch associated reviews
    associated_reviews = []
    if APP_STATE["reviews_df"] is not None:
        r_df = APP_STATE["reviews_df"]
        rev_match = r_df[r_df["product_id"].str.upper() == product_id.strip().upper()]
        associated_reviews = rev_match.to_dict(orient="records")

    return jsonify({
        "product": product_data,
        "reviews": associated_reviews,
        "review_count": len(associated_reviews),
        "disclaimer": SAFETY_DISCLAIMER,
    }), 200


@app.route("/api/recommend", methods=["POST"])
def get_recommendations():
    """Calculates personalized content-based product recommendations."""
    if APP_STATE["recommender"] is None:
        return jsonify({"error": "Recommender engine is not initialized."}), 503

    data = request.get_json(silent=True) or {}

    query = str(data.get("query", "")).strip()
    preferred_ingredients = data.get("preferred_ingredients", [])
    excluded_ingredients = data.get("excluded_ingredients", [])
    category = data.get("category")
    max_budget = data.get("max_budget")
    top_k = data.get("top_k", DEFAULT_TOP_K)

    # Sanitize and validate inputs
    if not isinstance(preferred_ingredients, list):
        preferred_ingredients = [str(preferred_ingredients)]
    if not isinstance(excluded_ingredients, list):
        excluded_ingredients = [str(excluded_ingredients)]

    # Clean empty tokens
    preferred_ingredients = [str(i).strip() for i in preferred_ingredients if str(i).strip()]
    excluded_ingredients = [str(i).strip() for i in excluded_ingredients if str(i).strip()]

    try:
        max_budget = float(max_budget) if max_budget not in (None, "") else None
        if max_budget is not None and max_budget <= 0:
            return jsonify({"error": "max_budget must be a positive number."}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid max_budget format."}), 400

    try:
        top_k = int(top_k)
        top_k = min(max(1, top_k), MAX_TOP_K)
    except (ValueError, TypeError):
        top_k = DEFAULT_TOP_K

    try:
        results = APP_STATE["recommender"].recommend(
            query=query,
            preferred_ingredients=preferred_ingredients,
            excluded_ingredients=excluded_ingredients,
            category=category,
            max_budget=max_budget,
            top_k=top_k,
        )
        return jsonify(results), 200
    except Exception as e:
        logger.exception(f"Recommendation generation error: {e}")
        return jsonify({"error": "An internal error occurred while processing recommendations."}), 500


@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    """Returns analytics and paginated customer reviews."""
    if APP_STATE["reviews_df"] is None:
        return jsonify({"error": "Reviews data unavailable."}), 503

    product_id = request.args.get("product_id")
    sentiment = request.args.get("sentiment")
    min_rating = request.args.get("min_rating", type=float)
    search = request.args.get("search")
    page = max(1, request.args.get("page", 1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", 15, type=int)))

    analytics = get_review_analytics(
        reviews_df=APP_STATE["reviews_df"],
        product_id=product_id,
        sentiment=sentiment,
        min_rating=min_rating,
        search=search,
        page=page,
        per_page=per_page,
    )
    return jsonify(analytics), 200


@app.route("/api/sentiment/predict", methods=["POST"])
def predict_sentiment():
    """Predicts sentiment label and class probabilities for a review text."""
    if APP_STATE["sentiment_pipeline"] is None:
        return jsonify({"error": "Sentiment model is not initialized."}), 503

    data = request.get_json(silent=True) or {}
    text = data.get("review_text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Field 'review_text' must be a non-empty string."}), 400

    try:
        prediction_result = APP_STATE["sentiment_pipeline"].predict(text)
        return jsonify(prediction_result), 200
    except Exception as e:
        logger.exception(f"Sentiment prediction error: {e}")
        return jsonify({"error": "Internal error during sentiment inference."}), 500


@app.route("/api/evaluation", methods=["GET"])
def get_evaluation():
    """Returns computed held-out evaluation metrics for both models."""
    if APP_STATE["evaluation_metrics"] is not None:
        return jsonify(APP_STATE["evaluation_metrics"]), 200

    if EVALUATION_METRICS_PATH.exists():
        with open(EVALUATION_METRICS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            APP_STATE["evaluation_metrics"] = data
            return jsonify(data), 200

    return jsonify({
        "status": "not_evaluated_yet",
        "message": "Evaluation metrics are not available. Please run 'python run_pipeline.py'.",
    }), 200


@app.route("/api/eda/charts", methods=["GET"])
def get_eda_charts():
    """Returns available EDA visualization chart filenames and titles."""
    charts = [
        {
            "id": "category",
            "title": "Catalogue Distribution by Skincare Category",
            "filename": "eda_category_distribution.png",
            "url": "/static/img/eda/eda_category_distribution.png",
            "description": "Horizontal bar breakdown of catalogue depth across all 8 skincare product categories.",
        },
        {
            "id": "price",
            "title": "Retail Price Distribution (USD)",
            "filename": "eda_price_distribution.png",
            "url": "/static/img/eda/eda_price_distribution.png",
            "description": "Kernel Density Estimation and histogram showing median price points and budget spread.",
        },
        {
            "id": "rating",
            "title": "Product Rating Variation by Category",
            "filename": "eda_rating_distribution.png",
            "url": "/static/img/eda/eda_rating_distribution.png",
            "description": "Box plot demonstrating rating spreads, interquartile ranges, and outlier patterns.",
        },
        {
            "id": "sentiment",
            "title": "Customer Review Sentiment Breakdown",
            "filename": "eda_sentiment_distribution.png",
            "url": "/static/img/eda/eda_sentiment_distribution.png",
            "description": "Class distribution of positive, neutral, and negative customer review experiences.",
        },
        {
            "id": "missingness",
            "title": "Data Pipeline Completeness (%)",
            "filename": "eda_missingness.png",
            "url": "/static/img/eda/eda_missingness.png",
            "description": "Verification of 100% data completeness post-cleaning across all required schema fields.",
        },
    ]
    return jsonify({"charts": charts}), 200


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def handle_not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found", "status_code": 404}), 404
    return render_template("index.html"), 404


@app.errorhandler(500)
def handle_server_error(e):
    logger.exception(f"Unhandled 500 error: {e}")
    return jsonify({
        "error": "An internal server error occurred.",
        "status_code": 500,
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print(f"Starting GlowRight Web Application on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
