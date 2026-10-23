"""Configuration settings and constants for the GlowRight application."""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
MODELS_DIR = BASE_DIR / "models"
WEB_DIR = BASE_DIR / "web"
STATIC_DIR = WEB_DIR / "static"
EDA_IMG_DIR = STATIC_DIR / "img" / "eda"

# Data file paths
RAW_PRODUCTS_PATH = DATA_DIR / "products_demo.csv"
RAW_REVIEWS_PATH = DATA_DIR / "reviews_demo.csv"
CLEAN_PRODUCTS_PATH = OUTPUTS_DIR / "cleaned_products.csv"
CLEAN_REVIEWS_PATH = OUTPUTS_DIR / "cleaned_reviews.csv"
DATA_SUMMARY_PATH = OUTPUTS_DIR / "data_summary.json"
EVALUATION_METRICS_PATH = MODELS_DIR / "evaluation_metrics.json"

# Model paths
SENTIMENT_MODEL_PATH = MODELS_DIR / "sentiment_model.joblib"
SENTIMENT_VEC_PATH = MODELS_DIR / "sentiment_vectorizer.joblib"
RECOMMENDER_MODEL_PATH = MODELS_DIR / "recommender_tfidf.joblib"

# Required schemas
REQUIRED_PRODUCT_COLUMNS = [
    "product_id",
    "product_name",
    "brand",
    "category",
    "price",
    "rating",
    "review_count",
    "ingredients",
    "description",
]

REQUIRED_REVIEW_COLUMNS = [
    "review_id",
    "product_id",
    "rating",
    "review_text",
]

VALID_CATEGORIES = [
    "Cleanser",
    "Serum",
    "Moisturizer",
    "Sunscreen",
    "Toner",
    "Exfoliant",
    "Eye Cream",
    "Mask",
]

VALID_SENTIMENTS = ["positive", "neutral", "negative"]

# Machine Learning & Recommendation Parameters
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
MIN_PRICE = 0.0
MAX_PRICE_CAP = 1000.0

TFIDF_MAX_FEATURES = 1500
TFIDF_NGRAM_RANGE = (1, 2)
RANDOM_STATE = 42

# Safety & Ethical Disclaimers
SAFETY_DISCLAIMER = (
    "Educational & Exploratory Prototype: GlowRight provides content-based product "
    "matching and sentiment analysis for academic/internship demonstration only. "
    "It does NOT provide clinical advice, diagnose dermatological conditions, "
    "or guarantee personal skin tolerance or hypoallergenic status. "
    "Consult a board-certified dermatologist for medical skincare concerns."
)

DEMO_DATA_NOTICE = (
    "Demonstration Dataset: The current dataset contains curated synthetic records "
    "specifically designed for benchmarking recommendation algorithms and sentiment models. "
    "Values do not represent commercial brand endorsements or clinical trial outcomes."
)
