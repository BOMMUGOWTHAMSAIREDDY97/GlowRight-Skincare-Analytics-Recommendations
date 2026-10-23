"""Exploratory Data Analysis (EDA) module for GlowRight.
Generates publication-quality charts using project palette (sage-green, terracotta, warm cream).
"""

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd
import matplotlib
# Use non-interactive backend for headless server execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from src.config import (
    CLEAN_PRODUCTS_PATH,
    CLEAN_REVIEWS_PATH,
    OUTPUTS_DIR,
    EDA_IMG_DIR,
)

logger = logging.getLogger(__name__)

# Design System Palette
PALETTE = {
    "primary": "#4A6B5D",     # Sage Green
    "secondary": "#C86D51",   # Muted Terracotta
    "accent": "#8FA89B",      # Soft Sage
    "cream": "#FAF8F5",       # Warm Cream
    "dark": "#242B28",        # Deep Charcoal
    "card_bg": "#FFFFFF",
    "grid": "#E8E5DF",
    "positive": "#4A6B5D",
    "neutral": "#D4A373",
    "negative": "#C86D51",
}

def set_aesthetic_style():
    """Sets a clean, modern aesthetic style for matplotlib."""
    plt.rcParams.update({
        "figure.facecolor": PALETTE["cream"],
        "axes.facecolor": PALETTE["card_bg"],
        "axes.edgecolor": "#DCD7D0",
        "axes.labelcolor": PALETTE["dark"],
        "text.color": PALETTE["dark"],
        "xtick.color": PALETTE["dark"],
        "ytick.color": PALETTE["dark"],
        "grid.color": PALETTE["grid"],
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
        "font.family": "sans-serif",
        "font.size": 10,
    })


def generate_category_chart(products_df: pd.DataFrame, save_dirs: List[Path]) -> str:
    """Generates bar chart of product counts by category."""
    plt.figure(figsize=(8, 4.5), dpi=150)
    counts = products_df["category"].value_counts().sort_values(ascending=True)
    
    colors = [PALETTE["accent"] if i < len(counts) - 1 else PALETTE["primary"] for i in range(len(counts))]
    bars = plt.barh(counts.index, counts.values, color=colors, edgecolor="none", height=0.65)
    
    plt.title("Catalogue Distribution Across Skincare Categories", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Number of Products", fontsize=10, labelpad=8)
    plt.grid(axis="x", alpha=0.5)
    
    # Value annotations
    for bar in bars:
        w = bar.get_width()
        plt.text(w + 0.3, bar.get_y() + bar.get_height() / 2, f"{int(w)}",
                 va="center", ha="left", fontsize=9, fontweight="bold", color=PALETTE["dark"])

    plt.tight_layout()
    filename = "eda_category_distribution.png"
    for d in save_dirs:
        plt.savefig(d / filename, bbox_inches="tight")
    plt.close()
    return filename


def generate_price_chart(products_df: pd.DataFrame, save_dirs: List[Path]) -> str:
    """Generates histogram with KDE for product prices."""
    plt.figure(figsize=(8, 4.5), dpi=150)
    
    sns.histplot(
        products_df["price"],
        kde=True,
        color=PALETTE["secondary"],
        edgecolor=PALETTE["card_bg"],
        bins=12,
        alpha=0.65,
    )
    
    median_price = products_df["price"].median()
    plt.axvline(median_price, color=PALETTE["dark"], linestyle="--", linewidth=1.5,
                label=f"Median: ${median_price:.2f}")
    
    plt.title("Retail Price Distribution (USD)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Price in USD ($)", fontsize=10, labelpad=8)
    plt.ylabel("Frequency", fontsize=10, labelpad=8)
    plt.legend(frameon=True, facecolor=PALETTE["cream"], edgecolor="none")
    plt.grid(alpha=0.5)

    plt.tight_layout()
    filename = "eda_price_distribution.png"
    for d in save_dirs:
        plt.savefig(d / filename, bbox_inches="tight")
    plt.close()
    return filename


def generate_rating_chart(products_df: pd.DataFrame, save_dirs: List[Path]) -> str:
    """Generates distribution chart for product ratings."""
    plt.figure(figsize=(8, 4.5), dpi=150)
    
    sns.boxplot(
        x="category",
        y="rating",
        data=products_df,
        hue="category",
        legend=False,
        palette="Greens_d",
        width=0.5,
        fliersize=3,
    )
    
    plt.title("Product Rating Variation by Category", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Category", fontsize=10, labelpad=8)
    plt.ylabel("Average Customer Rating (out of 5)", fontsize=10, labelpad=8)
    plt.xticks(rotation=25, ha="right")
    plt.ylim(3.8, 5.1)
    plt.grid(axis="y", alpha=0.5)

    plt.tight_layout()
    filename = "eda_rating_distribution.png"
    for d in save_dirs:
        plt.savefig(d / filename, bbox_inches="tight")
    plt.close()
    return filename


def generate_sentiment_chart(reviews_df: pd.DataFrame, save_dirs: List[Path]) -> str:
    """Generates customer review sentiment breakdown."""
    plt.figure(figsize=(8, 4.5), dpi=150)
    
    counts = reviews_df["sentiment"].value_counts()
    categories = [s for s in ["positive", "neutral", "negative"] if s in counts.index]
    values = [counts[s] for s in categories]
    colors = [PALETTE[s] for s in categories]

    bars = plt.bar(categories, values, color=colors, width=0.5, edgecolor="none")
    plt.title("Customer Review Sentiment Distribution", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("Review Count", fontsize=10, labelpad=8)
    plt.xlabel("Sentiment Class", fontsize=10, labelpad=8)
    plt.grid(axis="y", alpha=0.5)

    total = sum(values)
    for bar in bars:
        h = bar.get_height()
        pct = (h / total) * 100 if total > 0 else 0
        plt.text(bar.get_x() + bar.get_width() / 2, h + 1, f"{int(h)} ({pct:.1f}%)",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    filename = "eda_sentiment_distribution.png"
    for d in save_dirs:
        plt.savefig(d / filename, bbox_inches="tight")
    plt.close()
    return filename


def generate_missingness_chart(products_df: pd.DataFrame, reviews_df: pd.DataFrame, save_dirs: List[Path]) -> str:
    """Generates data completeness / missingness visualization."""
    plt.figure(figsize=(8, 4.5), dpi=150)
    
    # Compute missing percentages
    p_nulls = products_df.isnull().mean() * 100
    r_nulls = reviews_df.isnull().mean() * 100
    
    features = list(p_nulls.index[:6]) + [f"rev_{c}" for c in r_nulls.index[:4]]
    completeness = [100 - p_nulls[c] for c in p_nulls.index[:6]] + [100 - r_nulls[c] for c in r_nulls.index[:4]]

    bars = plt.barh(features, completeness, color=PALETTE["primary"], height=0.55)
    plt.xlim(0, 110)
    plt.title("Feature Completeness After Pipeline Cleaning (%)", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Data Completeness Rate (%)", fontsize=10, labelpad=8)
    plt.grid(axis="x", alpha=0.5)

    for bar in bars:
        w = bar.get_width()
        plt.text(w + 1, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%",
                 va="center", ha="left", fontsize=8, fontweight="bold")

    plt.tight_layout()
    filename = "eda_missingness.png"
    for d in save_dirs:
        plt.savefig(d / filename, bbox_inches="tight")
    plt.close()
    return filename


def run_eda(
    products_path: Path = CLEAN_PRODUCTS_PATH,
    reviews_path: Path = CLEAN_REVIEWS_PATH,
    outputs_dir: Path = OUTPUTS_DIR,
    web_eda_dir: Path = EDA_IMG_DIR,
) -> Dict[str, str]:
    """Generates all EDA visualization figures."""
    logger.info("Executing EDA visual analysis generation...")
    outputs_dir.mkdir(parents=True, exist_ok=True)
    web_eda_dir.mkdir(parents=True, exist_ok=True)
    save_dirs = [outputs_dir, web_eda_dir]

    set_aesthetic_style()

    products_df = pd.read_csv(products_path)
    reviews_df = pd.read_csv(reviews_path)

    charts = {}
    charts["category"] = generate_category_chart(products_df, save_dirs)
    charts["price"] = generate_price_chart(products_df, save_dirs)
    charts["rating"] = generate_rating_chart(products_df, save_dirs)
    charts["sentiment"] = generate_sentiment_chart(reviews_df, save_dirs)
    charts["missingness"] = generate_missingness_chart(products_df, reviews_df, save_dirs)

    logger.info(f"Generated {len(charts)} EDA visual charts.")
    return charts
