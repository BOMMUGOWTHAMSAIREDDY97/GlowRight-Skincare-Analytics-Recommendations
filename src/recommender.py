"""Content-based recommendation engine for GlowRight.
Combines TF-IDF text vectorization, cosine similarity, hard ingredient exclusion,
and budget/category constraints with explainable match rationales.
"""

import logging
import re
from typing import List, Dict, Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import (
    RECOMMENDER_MODEL_PATH,
    CLEAN_PRODUCTS_PATH,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
    DEFAULT_TOP_K,
    MAX_TOP_K,
    SAFETY_DISCLAIMER,
)

logger = logging.getLogger(__name__)


class ContentRecommender:
    """Content-based skincare recommender using TF-IDF and Cosine Similarity."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None
        self.products_df: Optional[pd.DataFrame] = None
        self.is_fitted: bool = False

    def fit(self, products_df: pd.DataFrame) -> "ContentRecommender":
        """Fits TF-IDF vectorizer on products content text."""
        self.products_df = products_df.copy().reset_index(drop=True)
        
        # Ensure content_text is created
        if "content_text" not in self.products_df.columns:
            self.products_df["content_text"] = (
                self.products_df["product_name"] + " " +
                self.products_df["brand"] + " " +
                self.products_df["category"] + " " +
                self.products_df["description"] + " " +
                self.products_df["ingredients_normalized"]
            )

        self.vectorizer = TfidfVectorizer(
            max_features=TFIDF_MAX_FEATURES,
            ngram_range=TFIDF_NGRAM_RANGE,
            stop_words="english",
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.products_df["content_text"])
        self.is_fitted = True
        logger.info(f"Recommender fitted on {len(self.products_df)} products.")
        return self

    def save(self, model_path=RECOMMENDER_MODEL_PATH) -> None:
        """Serializes recommender model and vectorizer."""
        if not self.is_fitted:
            raise ValueError("Recommender is not fitted yet.")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "tfidf_matrix": self.tfidf_matrix,
                "products_df": self.products_df,
            },
            model_path,
        )
        logger.info(f"Recommender saved to {model_path}")

    @classmethod
    def load(cls, model_path=RECOMMENDER_MODEL_PATH) -> "ContentRecommender":
        """Loads serialized recommender model."""
        if not model_path.exists():
            raise FileNotFoundError(f"Recommender model file not found at {model_path}")
        payload = joblib.load(model_path)
        recommender = cls()
        recommender.vectorizer = payload["vectorizer"]
        recommender.tfidf_matrix = payload["tfidf_matrix"]
        recommender.products_df = payload["products_df"]
        recommender.is_fitted = True
        return recommender

    def _matches_exclusion(self, ingredients_text: str, excluded_list: List[str]) -> bool:
        """Returns True if the ingredients text contains any excluded ingredient."""
        if not excluded_list:
            return False
        ing_lower = str(ingredients_text).lower()
        for excl in excluded_list:
            excl_clean = excl.strip().lower()
            if not excl_clean:
                continue
            # Regex word boundary or substring match
            pattern = r"(^|[,\s\(\)])" + re.escape(excl_clean) + r"([,\s\(\)]|$)"
            if re.search(pattern, ing_lower) or excl_clean in ing_lower:
                return True
        return False

    def _extract_match_reasons(
        self,
        product: pd.Series,
        query: str,
        preferred_ingredients: List[str],
        category: Optional[str],
    ) -> List[str]:
        """Generates transparent, human-readable explanations for product matching."""
        reasons = []
        ing_lower = str(product.get("ingredients_normalized", "")).lower()

        # Preferred ingredients matched
        matched_prefs = []
        for pref in preferred_ingredients:
            pref_clean = pref.strip()
            if pref_clean and pref_clean.lower() in ing_lower:
                matched_prefs.append(pref_clean)
        if matched_prefs:
            reasons.append(f"Contains requested ingredient(s): {', '.join(matched_prefs)}")

        # Category match
        if category and category.lower() != "all" and product["category"].lower() == category.lower():
            reasons.append(f"Matches desired category: {product['category']}")

        # Query keywords overlap
        if query:
            tokens = [t.lower() for t in re.findall(r"\b[a-zA-Z]{3,}\b", query)]
            prod_text = (
                str(product.get("product_name", "")) + " " +
                str(product.get("description", ""))
            ).lower()
            matched_words = [t for t in tokens if t in prod_text]
            if matched_words:
                unique_words = list(dict.fromkeys(matched_words))[:3]
                reasons.append(f"Aligns with query attributes: '{', '.join(unique_words)}'")

        # High rating badge if 4.7+
        if float(product.get("rating", 0.0)) >= 4.7:
            reasons.append(f"Top community rated: {product['rating']}★")

        if not reasons:
            reasons.append("Best content profile match within your criteria")

        return reasons

    def recommend(
        self,
        query: str = "",
        preferred_ingredients: Optional[List[str]] = None,
        excluded_ingredients: Optional[List[str]] = None,
        category: Optional[str] = None,
        max_budget: Optional[float] = None,
        top_k: int = DEFAULT_TOP_K,
    ) -> Dict[str, Any]:
        """Recommends products matching user criteria with similarity scores and baseline comparison."""
        if not self.is_fitted:
            raise ValueError("Recommender must be fitted or loaded before querying.")

        preferred_ingredients = preferred_ingredients or []
        excluded_ingredients = excluded_ingredients or []
        top_k = min(max(1, int(top_k)), MAX_TOP_K)

        df = self.products_df.copy()
        total_catalogue_count = len(df)

        # 1. HARD FILTERS (Budget, Category, Excluded Ingredients)
        if max_budget is not None and max_budget > 0:
            df = df[df["price"] <= float(max_budget)]

        if category and category.strip() and category.lower() != "all":
            df = df[df["category"].str.lower() == category.strip().lower()]

        if excluded_ingredients:
            df = df[~df["ingredients_normalized"].apply(
                lambda x: self._matches_exclusion(x, excluded_ingredients)
            )]

        filtered_count = len(df)

        # Handle zero candidates after hard filtering
        if filtered_count == 0:
            return {
                "recommendations": [],
                "baseline_popular": [],
                "metadata": {
                    "total_catalogue": total_catalogue_count,
                    "candidates_after_filters": 0,
                    "query": query,
                    "applied_filters": {
                        "category": category,
                        "max_budget": max_budget,
                        "preferred_ingredients": preferred_ingredients,
                        "excluded_ingredients": excluded_ingredients,
                    },
                    "message": "No products met all hard filter criteria (budget, category, and ingredient exclusions). Try broadening your search or relaxing ingredient exclusions.",
                },
                "disclaimer": SAFETY_DISCLAIMER,
            }

        # 2. POPULARITY/RATING BASELINE (for comparison)
        # Weighted rating = rating * log10(review_count + 10)
        baseline_df = df.copy()
        baseline_df["popularity_score"] = (
            baseline_df["rating"] * np.log10(baseline_df["review_count"] + 10)
        )
        top_baseline = baseline_df.sort_values(
            by=["popularity_score", "rating"], ascending=False
        ).head(top_k)

        baseline_results = []
        for _, row in top_baseline.iterrows():
            baseline_results.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "brand": row["brand"],
                "category": row["category"],
                "price": float(row["price"]),
                "rating": float(row["rating"]),
                "review_count": int(row["review_count"]),
                "ingredients": row["ingredients_normalized"],
                "is_demo": bool(row.get("is_demo", True)),
                "baseline_metric": "Popularity & Customer Rating Rank",
            })

        # 3. CONTENT-BASED RANKING
        # Build enriched user profile string
        profile_parts = []
        if query and query.strip():
            profile_parts.append(query.strip())
        if preferred_ingredients:
            # Emphasize preferred ingredients by repeating
            profile_parts.append(" ".join(preferred_ingredients) * 2)

        user_profile_text = " ".join(profile_parts).strip()

        # If user provided no query and no preferred ingredients, fall back to baseline
        if not user_profile_text:
            return {
                "recommendations": baseline_results,
                "baseline_popular": baseline_results,
                "metadata": {
                    "total_catalogue": total_catalogue_count,
                    "candidates_after_filters": filtered_count,
                    "query": "",
                    "applied_filters": {
                        "category": category,
                        "max_budget": max_budget,
                        "preferred_ingredients": preferred_ingredients,
                        "excluded_ingredients": excluded_ingredients,
                    },
                    "message": "No specific query or preferred ingredients provided; displaying top community-rated products matching your filters.",
                },
                "disclaimer": SAFETY_DISCLAIMER,
            }

        # Vectorize user profile
        user_vector = self.vectorizer.transform([user_profile_text])
        
        # Sub-matrix of candidate items
        candidate_indices = df.index.to_numpy()
        candidate_matrix = self.tfidf_matrix[candidate_indices]
        
        # Compute Cosine Similarities
        similarities = cosine_similarity(user_vector, candidate_matrix).flatten()
        df["similarity_score"] = similarities

        # Sort by similarity score descending, tie-break by rating
        top_df = df.sort_values(
            by=["similarity_score", "rating"], ascending=[False, False]
        ).head(top_k)

        recommendations = []
        for _, row in top_df.iterrows():
            sim_score = float(row["similarity_score"])
            reasons = self._extract_match_reasons(
                row, query, preferred_ingredients, category
            )
            recommendations.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "brand": row["brand"],
                "category": row["category"],
                "price": float(row["price"]),
                "rating": float(row["rating"]),
                "review_count": int(row["review_count"]),
                "similarity_score": round(sim_score, 4),
                "ingredients": row["ingredients_normalized"],
                "description": row["description"],
                "match_reasons": reasons,
                "is_demo": bool(row.get("is_demo", True)),
            })

        return {
            "recommendations": recommendations,
            "baseline_popular": baseline_results,
            "metadata": {
                "total_catalogue": total_catalogue_count,
                "candidates_after_filters": filtered_count,
                "query": query,
                "applied_filters": {
                    "category": category,
                    "max_budget": max_budget,
                    "preferred_ingredients": preferred_ingredients,
                    "excluded_ingredients": excluded_ingredients,
                },
                "ranking_method": "TF-IDF Vector Space with Cosine Similarity",
            },
            "disclaimer": SAFETY_DISCLAIMER,
        }
