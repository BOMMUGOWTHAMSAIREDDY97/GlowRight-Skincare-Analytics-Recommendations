"""Sentiment classification module for customer skincare reviews.
Implements a leakage-free TF-IDF + Logistic Regression pipeline,
evaluated against a majority-class baseline with held-out splits.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from src.config import (
    SENTIMENT_MODEL_PATH,
    SENTIMENT_VEC_PATH,
    CLEAN_REVIEWS_PATH,
    VALID_SENTIMENTS,
    RANDOM_STATE,
    SAFETY_DISCLAIMER,
)

logger = logging.getLogger(__name__)


class SentimentClassifierPipeline:
    """Supervised Sentiment Classification Pipeline with Leakage Prevention."""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.model: Optional[LogisticRegression] = None
        self.baseline_model: Optional[DummyClassifier] = None
        self.classes_: Optional[np.ndarray] = None
        self.evaluation_results: Dict[str, Any] = {}
        self.is_trained: bool = False

    def train_and_evaluate(
        self,
        reviews_df: pd.DataFrame,
        test_size: float = 0.25,
        random_state: int = RANDOM_STATE,
    ) -> Dict[str, Any]:
        """Trains Logistic Regression and Majority baseline using strict stratified train/test split.
        Vectorizers are fitted strictly on the training partition to prevent leakage.
        """
        # Filter valid text and sentiment
        df = reviews_df.dropna(subset=["review_text", "sentiment"]).copy()
        df = df[df["sentiment"].isin(VALID_SENTIMENTS)]

        if len(df) < 20:
            raise ValueError(
                f"Insufficient labeled reviews ({len(df)}) for reliable model training."
            )

        X = df["review_text"].astype(str)
        y = df["sentiment"].astype(str)

        # Stratified train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )

        logger.info(
            f"Sentiment training split: {len(X_train)} train samples, {len(X_test)} test samples."
        )

        # 1. FIT VECTORIZER ONLY ON TRAINING DATA (No data leakage)
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)

        # 2. MAJORITY BASELINE MODEL
        self.baseline_model = DummyClassifier(strategy="most_frequent")
        self.baseline_model.fit(X_train_vec, y_train)
        baseline_preds = self.baseline_model.predict(X_test_vec)
        baseline_acc = float(accuracy_score(y_test, baseline_preds))
        baseline_f1 = float(f1_score(y_test, baseline_preds, average="macro", zero_division=0))

        # 3. LOGISTIC REGRESSION (Primary Model)
        self.model = LogisticRegression(
            C=1.0,
            class_weight="balanced",
            max_iter=1000,
            random_state=random_state,
        )
        self.model.fit(X_train_vec, y_train)
        self.classes_ = self.model.classes_

        y_pred = self.model.predict(X_test_vec)

        # 4. MULTINOMIAL NAIVE BAYES (Benchmark Comparison)
        nb_model = MultinomialNB(alpha=1.0)
        nb_model.fit(X_train_vec, y_train)
        nb_preds = nb_model.predict(X_test_vec)
        nb_acc = float(accuracy_score(y_test, nb_preds))
        nb_f1 = float(f1_score(y_test, nb_preds, average="macro", zero_division=0))

        # 5. HELD-OUT EVALUATION METRICS
        labels_order = [c for c in ["positive", "neutral", "negative"] if c in self.classes_]
        
        acc = float(accuracy_score(y_test, y_pred))
        macro_prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
        macro_rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
        macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))

        # Per-class metrics
        per_class_report = classification_report(
            y_test, y_pred, labels=labels_order, output_dict=True, zero_division=0
        )

        cm = confusion_matrix(y_test, y_pred, labels=labels_order)

        # Collect error analysis samples
        test_df = pd.DataFrame({
            "review_text": X_test,
            "true_sentiment": y_test,
            "pred_sentiment": y_pred,
        })
        errors = test_df[test_df["true_sentiment"] != test_df["pred_sentiment"]].head(5).to_dict(
            orient="records"
        )

        self.evaluation_results = {
            "model_type": "TF-IDF + Logistic Regression (class_weight='balanced')",
            "dataset_split": {
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "total_samples": len(df),
                "class_distribution_train": y_train.value_counts().to_dict(),
                "class_distribution_test": y_test.value_counts().to_dict(),
            },
            "metrics": {
                "accuracy": round(acc, 4),
                "macro_precision": round(macro_prec, 4),
                "macro_recall": round(macro_rec, 4),
                "macro_f1": round(macro_f1, 4),
            },
            "per_class": {
                label: {
                    "precision": round(per_class_report[label]["precision"], 4),
                    "recall": round(per_class_report[label]["recall"], 4),
                    "f1_score": round(per_class_report[label]["f1-score"], 4),
                    "support": int(per_class_report[label]["support"]),
                }
                for label in labels_order if label in per_class_report
            },
            "confusion_matrix": {
                "labels": labels_order,
                "matrix": cm.tolist(),
            },
            "baseline_comparison": {
                "majority_baseline": {
                    "accuracy": round(baseline_acc, 4),
                    "macro_f1": round(baseline_f1, 4),
                },
                "multinomial_nb": {
                    "accuracy": round(nb_acc, 4),
                    "macro_f1": round(nb_f1, 4),
                },
                "logistic_regression": {
                    "accuracy": round(acc, 4),
                    "macro_f1": round(macro_f1, 4),
                },
            },
            "error_analysis_samples": errors,
            "limitations_note": (
                "Evaluated on synthetic benchmark demo reviews. In real clinical scenarios, "
                "customer sentiment reflects cosmetic satisfaction rather than medical efficacy."
            ),
        }

        self.is_trained = True
        return self.evaluation_results

    def save(
        self,
        model_path: Path = SENTIMENT_MODEL_PATH,
        vec_path: Path = SENTIMENT_VEC_PATH,
    ) -> None:
        """Saves trained model and vectorizer safely to disk."""
        if not self.is_trained:
            raise ValueError("Model is not trained. Call train_and_evaluate first.")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, model_path)
        joblib.dump(self.vectorizer, vec_path)
        logger.info(f"Saved sentiment artifacts to {model_path} and {vec_path}")

    @classmethod
    def load(
        cls,
        model_path: Path = SENTIMENT_MODEL_PATH,
        vec_path: Path = SENTIMENT_VEC_PATH,
    ) -> "SentimentClassifierPipeline":
        """Loads fitted sentiment classifier and vectorizer."""
        if not model_path.exists() or not vec_path.exists():
            raise FileNotFoundError("Sentiment model or vectorizer file not found.")
        pipeline = cls()
        pipeline.model = joblib.load(model_path)
        pipeline.vectorizer = joblib.load(vec_path)
        pipeline.classes_ = pipeline.model.classes_
        pipeline.is_trained = True
        return pipeline

    def predict(self, text: str) -> Dict[str, Any]:
        """Predicts sentiment for an arbitrary review text with class probabilities."""
        if not self.is_trained:
            raise ValueError("Pipeline is not trained or loaded.")

        if not text or not str(text).strip():
            return {
                "prediction": "neutral",
                "confidence": 0.3333,
                "probabilities": {"positive": 0.33, "neutral": 0.34, "negative": 0.33},
                "warning": "Empty input provided; defaulted to neutral.",
            }

        vec = self.vectorizer.transform([text.strip()])
        pred = self.model.predict(vec)[0]
        
        # Calculate probabilities
        probs = self.model.predict_proba(vec)[0]
        prob_dict = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(self.model.classes_, probs)
        }
        confidence = float(np.max(probs))

        return {
            "prediction": str(pred),
            "confidence": round(confidence, 4),
            "probabilities": prob_dict,
            "input_text": text.strip(),
            "model_used": "TF-IDF + Logistic Regression",
            "is_demonstration": True,
            "disclaimer": SAFETY_DISCLAIMER,
        }
