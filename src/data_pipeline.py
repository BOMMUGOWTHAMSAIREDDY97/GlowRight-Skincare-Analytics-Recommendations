"""Data cleaning, validation, and pipeline processing module for GlowRight."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple

import pandas as pd
import numpy as np

from src.config import (
    RAW_PRODUCTS_PATH,
    RAW_REVIEWS_PATH,
    CLEAN_PRODUCTS_PATH,
    CLEAN_REVIEWS_PATH,
    DATA_SUMMARY_PATH,
    REQUIRED_PRODUCT_COLUMNS,
    REQUIRED_REVIEW_COLUMNS,
    VALID_CATEGORIES,
    VALID_SENTIMENTS,
    MIN_PRICE,
    MAX_PRICE_CAP,
    OUTPUTS_DIR,
)

logger = logging.getLogger(__name__)


class DataPipelineError(Exception):
    """Custom exception raised when pipeline validation fails."""
    pass


def normalize_ingredient_string(ingredients_text: str) -> str:
    """Standardizes ingredient list text while preserving chemical and INCI names."""
    if not isinstance(ingredients_text, str) or not ingredients_text.strip():
        return ""
    # Split by comma or semicolon, trim, remove internal double spaces
    tokens = [t.strip() for t in ingredients_text.replace(";", ",").split(",")]
    cleaned_tokens = []
    for token in tokens:
        # replace multiple internal spaces with single space
        norm = " ".join(token.split())
        if norm:
            cleaned_tokens.append(norm)
    return ", ".join(cleaned_tokens)


def validate_schema(df: pd.DataFrame, required_columns: list, dataset_name: str) -> None:
    """Validates that a DataFrame contains all required columns."""
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise DataPipelineError(
            f"Schema error in {dataset_name}: Missing required columns: {missing}"
        )


def clean_products_data(raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Cleans, validates, and standardizes products dataframe."""
    validate_schema(raw_df, REQUIRED_PRODUCT_COLUMNS, "Products")
    
    initial_count = len(raw_df)
    metrics = {
        "initial_product_count": initial_count,
        "duplicates_removed": 0,
        "invalid_prices_corrected": 0,
        "invalid_ratings_corrected": 0,
        "missing_values_imputed_or_dropped": 0,
    }

    df = raw_df.copy()

    # 1. Deduplicate by product_id
    dups = df.duplicated(subset=["product_id"], keep="first").sum()
    metrics["duplicates_removed"] = int(dups)
    df = df.drop_duplicates(subset=["product_id"], keep="first")

    # 2. Text cleaning: strip whitespace, string conversion
    text_cols = ["product_name", "brand", "category", "description", "ingredients"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()

    # Drop rows missing essential identifiers
    df = df[df["product_id"].astype(str).str.strip().str.len() > 0]
    df = df[df["product_name"].str.len() > 0]

    # 3. Category standardization (Title case, fallback to Other if unknown)
    df["category"] = df["category"].apply(
        lambda c: c if c in VALID_CATEGORIES else "Other"
    )

    # 4. Numeric validation: price
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    invalid_price_mask = df["price"].isna() | (df["price"] < MIN_PRICE) | (df["price"] > MAX_PRICE_CAP)
    metrics["invalid_prices_corrected"] = int(invalid_price_mask.sum())
    # If invalid price, use median price for category or global median
    median_price = df.loc[~invalid_price_mask, "price"].median()
    if pd.isna(median_price):
        median_price = 25.0
    df.loc[invalid_price_mask, "price"] = round(median_price, 2)

    # 5. Numeric validation: rating (1.0 to 5.0)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    invalid_rating_mask = df["rating"].isna() | (df["rating"] < 1.0) | (df["rating"] > 5.0)
    metrics["invalid_ratings_corrected"] = int(invalid_rating_mask.sum())
    df.loc[invalid_rating_mask, "rating"] = 4.0

    # 6. Review count
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)
    df["review_count"] = df["review_count"].clip(lower=0)

    # 7. Ingredient normalization
    df["ingredients_normalized"] = df["ingredients"].apply(normalize_ingredient_string)
    # Searchable ingredients tokens (lowercase set string for fast queries)
    df["ingredients_search"] = df["ingredients_normalized"].str.lower()

    # 8. Combined content text for recommendation TF-IDF
    df["content_text"] = (
        df["product_name"] + " " +
        df["brand"] + " " +
        df["category"] + " " +
        df["description"] + " Ingredients: " +
        df["ingredients_normalized"]
    )

    # 9. Demo data flag preservation
    if "is_demo" not in df.columns:
        df["is_demo"] = True
    else:
        df["is_demo"] = df["is_demo"].astype(bool)

    metrics["final_product_count"] = len(df)
    return df, metrics


def clean_reviews_data(raw_df: pd.DataFrame, valid_product_ids: set) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Cleans, validates, and standardizes customer reviews dataframe."""
    validate_schema(raw_df, REQUIRED_REVIEW_COLUMNS, "Reviews")

    initial_count = len(raw_df)
    metrics = {
        "initial_review_count": initial_count,
        "duplicates_removed": 0,
        "invalid_ratings_corrected": 0,
        "orphaned_reviews_removed": 0,
        "missing_text_removed": 0,
    }

    df = raw_df.copy()

    # 1. Deduplicate by review_id
    dups = df.duplicated(subset=["review_id"], keep="first").sum()
    metrics["duplicates_removed"] = int(dups)
    df = df.drop_duplicates(subset=["review_id"], keep="first")

    # 2. Text clean
    df["review_text"] = df["review_text"].astype(str).str.strip()
    # Drop empty reviews
    empty_mask = df["review_text"].str.len() < 3
    metrics["missing_text_removed"] = int(empty_mask.sum())
    df = df[~empty_mask]

    # 3. Referential integrity: remove reviews for products that don't exist
    if valid_product_ids:
        orphaned = ~df["product_id"].isin(valid_product_ids)
        metrics["orphaned_reviews_removed"] = int(orphaned.sum())
        df = df[~orphaned]

    # 4. Rating validation (1.0 to 5.0)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    invalid_rating = df["rating"].isna() | (df["rating"] < 1.0) | (df["rating"] > 5.0)
    metrics["invalid_ratings_corrected"] = int(invalid_rating.sum())
    df.loc[invalid_rating, "rating"] = 3.0

    # 5. Sentiment label validation
    if "sentiment" in df.columns:
        df["sentiment"] = df["sentiment"].astype(str).str.lower().str.strip()
        # map unknown sentiments to neutral
        df["sentiment"] = df["sentiment"].apply(
            lambda s: s if s in VALID_SENTIMENTS else "neutral"
        )
    else:
        # Default label derived transparently from rating with clear note
        df["sentiment"] = df["rating"].apply(
            lambda r: "positive" if r >= 4.0 else ("negative" if r <= 2.0 else "neutral")
        )

    # 6. Date validation
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        df["date"] = df["date"].fillna("2026-01-01")
    else:
        df["date"] = "2026-01-01"

    if "is_demo" not in df.columns:
        df["is_demo"] = True
    else:
        df["is_demo"] = df["is_demo"].astype(bool)

    metrics["final_review_count"] = len(df)
    return df, metrics


def run_data_pipeline(
    raw_products_path: Path = RAW_PRODUCTS_PATH,
    raw_reviews_path: Path = RAW_REVIEWS_PATH,
    output_dir: Path = OUTPUTS_DIR,
) -> Dict[str, Any]:
    """Orchestrates data loading, schema checks, cleaning, and persistence."""
    logger.info("Starting data pipeline execution...")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not raw_products_path.exists():
        raise FileNotFoundError(f"Raw products file not found: {raw_products_path}")
    if not raw_reviews_path.exists():
        raise FileNotFoundError(f"Raw reviews file not found: {raw_reviews_path}")

    # Load raw
    raw_products = pd.read_csv(raw_products_path)
    raw_reviews = pd.read_csv(raw_reviews_path)

    # Clean products
    cleaned_products, product_metrics = clean_products_data(raw_products)
    valid_pids = set(cleaned_products["product_id"].unique())

    # Clean reviews
    cleaned_reviews, review_metrics = clean_reviews_data(raw_reviews, valid_pids)

    # Save cleaned files
    cleaned_products.to_csv(CLEAN_PRODUCTS_PATH, index=False)
    cleaned_reviews.to_csv(CLEAN_REVIEWS_PATH, index=False)

    summary = {
        "pipeline_status": "success",
        "data_provenance": "Synthetic Benchmark Demonstration Data",
        "is_synthetic_demonstration": True,
        "products": product_metrics,
        "reviews": review_metrics,
        "category_counts": cleaned_products["category"].value_counts().to_dict(),
        "sentiment_counts": cleaned_reviews["sentiment"].value_counts().to_dict(),
        "average_product_price": round(float(cleaned_products["price"].mean()), 2),
        "average_product_rating": round(float(cleaned_products["rating"].mean()), 2),
        "output_files": {
            "cleaned_products": str(CLEAN_PRODUCTS_PATH),
            "cleaned_reviews": str(CLEAN_REVIEWS_PATH),
        },
    }

    with open(DATA_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        f"Pipeline complete. Products: {len(cleaned_products)}, Reviews: {len(cleaned_reviews)}"
    )
    return summary
