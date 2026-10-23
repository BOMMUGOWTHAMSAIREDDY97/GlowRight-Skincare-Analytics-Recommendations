"""Customer review analytics and reporting module for GlowRight.
Extracts sentiment trends, rating distributions, and recurring skincare themes/n-grams.
"""

import logging
import re
from collections import Counter
from typing import Dict, Any, List, Optional

import pandas as pd
from src.config import SAFETY_DISCLAIMER

logger = logging.getLogger(__name__)

COMMON_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between",
    "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do",
    "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from",
    "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd",
    "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his",
    "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
    "ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll",
    "she's", "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the",
    "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they",
    "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
    "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
    "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "product", "skincare", "day", "days", "week", "weeks", "month", "months", "use", "used", "using"
}


def extract_review_themes(reviews_series: pd.Series, top_n: int = 10) -> List[Dict[str, Any]]:
    """Extracts frequent bi-gram and tri-gram skincare review phrases."""
    phrases = []
    for text in reviews_series.dropna():
        cleaned = re.sub(r"[^a-zA-Z\s]", "", str(text).lower())
        words = [w for w in cleaned.split() if len(w) > 2 and w not in COMMON_STOPWORDS]
        
        # 2-grams
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
        # 3-grams
        for i in range(len(words) - 2):
            phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")

    counts = Counter(phrases).most_common(top_n)
    return [{"theme": theme, "occurrences": count} for theme, count in counts]


def get_review_analytics(
    reviews_df: pd.DataFrame,
    product_id: Optional[str] = None,
    sentiment: Optional[str] = None,
    min_rating: Optional[float] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 20,
) -> Dict[str, Any]:
    """Computes comprehensive review metrics and paginated review listings."""
    df = reviews_df.copy()

    # Total counts before specific filtering
    total_reviews_all = len(df)
    global_sentiment_counts = df["sentiment"].value_counts().to_dict()
    global_rating_distribution = df["rating"].value_counts().sort_index().to_dict()

    # Apply filters
    if product_id and product_id.strip():
        df = df[df["product_id"].str.upper() == product_id.strip().upper()]

    if sentiment and sentiment.strip() and sentiment.lower() != "all":
        df = df[df["sentiment"].str.lower() == sentiment.strip().lower()]

    if min_rating is not None and min_rating > 0:
        df = df[df["rating"] >= float(min_rating)]

    if search and search.strip():
        q = search.strip().lower()
        df = df[df["review_text"].str.lower().str.contains(q, regex=False)]

    filtered_count = len(df)

    # Calculate filtered statistics
    avg_rating = round(float(df["rating"].mean()), 2) if not df.empty else 0.0
    filtered_sentiment_counts = df["sentiment"].value_counts().to_dict()
    filtered_rating_dist = {
        str(star): int(df["rating"].apply(lambda r: round(r) == star).sum())
        for star in [5, 4, 3, 2, 1]
    }

    # Extract top skincare themes from current filtered subset
    recurring_themes = extract_review_themes(df["review_text"], top_n=8)

    # Pagination
    total_pages = max(1, (filtered_count + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    paginated_records = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return {
        "summary": {
            "total_reviews": filtered_count,
            "catalogue_total_reviews": total_reviews_all,
            "average_rating": avg_rating,
            "sentiment_counts": filtered_sentiment_counts,
            "global_sentiment_counts": global_sentiment_counts,
            "rating_distribution": filtered_rating_dist,
            "recurring_themes": recurring_themes,
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_records": filtered_count,
        },
        "reviews": paginated_records,
        "disclaimer": SAFETY_DISCLAIMER + " Customer review sentiment indicates personal user satisfaction and does not constitute validated dermatological evidence.",
    }
