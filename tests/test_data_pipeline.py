"""Automated tests for data pipeline, cleaning, and schema validation."""

import pytest
import pandas as pd
import numpy as np

from src.data_pipeline import (
    clean_products_data,
    clean_reviews_data,
    normalize_ingredient_string,
    validate_schema,
    DataPipelineError,
)
from src.config import REQUIRED_PRODUCT_COLUMNS, REQUIRED_REVIEW_COLUMNS


def test_normalize_ingredient_string():
    raw = "  Aqua,   Glycerin ;  Niacinamide 10% ,   Ceramide NP  "
    normalized = normalize_ingredient_string(raw)
    assert normalized == "Aqua, Glycerin, Niacinamide 10%, Ceramide NP"
    assert normalize_ingredient_string("") == ""
    assert normalize_ingredient_string(None) == ""


def test_validate_schema_success():
    df = pd.DataFrame(columns=REQUIRED_PRODUCT_COLUMNS)
    # Should not raise
    validate_schema(df, REQUIRED_PRODUCT_COLUMNS, "Products")


def test_validate_schema_failure():
    df = pd.DataFrame(columns=["product_id", "product_name"])
    with pytest.raises(DataPipelineError) as exc_info:
        validate_schema(df, REQUIRED_PRODUCT_COLUMNS, "Products")
    assert "Missing required columns" in str(exc_info.value)


def test_clean_products_data_deduplication_and_ranges():
    raw_data = pd.DataFrame([
        {
            "product_id": "TEST-01",
            "product_name": "Test Serum",
            "brand": "TestBrand",
            "category": "Serum",
            "price": -10.0,  # invalid price
            "rating": 6.5,   # invalid rating
            "review_count": "50",
            "ingredients": "Aqua, Glycerin",
            "description": "A test serum description.",
            "is_demo": True,
        },
        {  # Duplicate product_id
            "product_id": "TEST-01",
            "product_name": "Test Serum Duplicate",
            "brand": "TestBrand",
            "category": "Serum",
            "price": 20.0,
            "rating": 4.5,
            "review_count": 10,
            "ingredients": "Aqua, Glycerin",
            "description": "Duplicate description.",
            "is_demo": True,
        },
        {
            "product_id": "TEST-02",
            "product_name": "Test Cleanser",
            "brand": "TestBrand",
            "category": "Cleanser",
            "price": 18.0,
            "rating": 4.2,
            "review_count": 25,
            "ingredients": "Aqua, Oat Kernel",
            "description": "A test cleanser.",
            "is_demo": True,
        },
    ])

    cleaned_df, metrics = clean_products_data(raw_data)

    assert len(cleaned_df) == 2  # duplicate removed
    assert metrics["duplicates_removed"] == 1
    assert metrics["invalid_prices_corrected"] == 1
    assert metrics["invalid_ratings_corrected"] == 1

    # Price should be non-negative
    assert (cleaned_df["price"] > 0).all()
    # Rating should be <= 5.0
    assert (cleaned_df["rating"] <= 5.0).all()
    # Content text column created
    assert "content_text" in cleaned_df.columns
    assert "ingredients_normalized" in cleaned_df.columns


def test_clean_reviews_data_validation():
    valid_pids = {"TEST-01", "TEST-02"}
    raw_reviews = pd.DataFrame([
        {
            "review_id": "REV-01",
            "product_id": "TEST-01",
            "rating": 5.0,
            "review_text": "Great product for sensitive skin!",
            "sentiment": "positive",
        },
        {  # Duplicate review_id
            "review_id": "REV-01",
            "product_id": "TEST-01",
            "rating": 5.0,
            "review_text": "Duplicate text",
            "sentiment": "positive",
        },
        {  # Orphaned review (product does not exist)
            "review_id": "REV-02",
            "product_id": "NON-EXISTENT",
            "rating": 4.0,
            "review_text": "Product does not exist",
            "sentiment": "neutral",
        },
        {  # Empty text
            "review_id": "REV-03",
            "product_id": "TEST-02",
            "rating": 3.0,
            "review_text": "  ",
            "sentiment": "neutral",
        },
    ])

    cleaned_df, metrics = clean_reviews_data(raw_reviews, valid_product_ids=valid_pids)

    assert len(cleaned_df) == 1
    assert metrics["duplicates_removed"] == 1
    assert metrics["orphaned_reviews_removed"] == 1
    assert metrics["missing_text_removed"] == 1
    assert cleaned_df.iloc[0]["review_id"] == "REV-01"
