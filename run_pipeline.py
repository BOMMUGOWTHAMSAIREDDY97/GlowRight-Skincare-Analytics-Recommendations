"""GlowRight Master Pipeline Runner.
Orchestrates data cleaning, EDA chart generation, recommender fitting,
sentiment model training with leakage-free splits, and metrics evaluation.
"""

import sys
import io
import logging
from pathlib import Path

# Force UTF-8 stdout on Windows shells if supported
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.data_pipeline import run_data_pipeline
from src.eda import run_eda
from src.evaluation import run_full_evaluation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_pipeline")


def main():
    print("=" * 70)
    print("  GlowRight: Ingredient-Aware Skincare Recommendation Pipeline")
    print("  Internship Data Science with Python Project")
    print("=" * 70)

    try:
        # Step 1: Data Cleaning and Validation
        print("\n[1/3] Running Data Ingestion & Preprocessing Pipeline...")
        summary = run_data_pipeline()
        print(f"  [+] Cleaned {summary['products']['final_product_count']} products.")
        print(f"  [+] Cleaned {summary['reviews']['final_review_count']} reviews.")
        print(f"  [+] Category counts: {summary['category_counts']}")

        # Step 2: Exploratory Data Analysis Visualizations
        print("\n[2/3] Generating EDA Visualizations...")
        charts = run_eda()
        for key, name in charts.items():
            print(f"  [+] Generated {key} chart -> {name}")

        # Step 3: Model Training and Honest Evaluation
        print("\n[3/3] Training Models & Executing Held-out Evaluation...")
        eval_results = run_full_evaluation()
        
        sent_metrics = eval_results["sentiment_classification"]["metrics"]
        rec_metrics = eval_results["content_recommender"]

        print("\n" + "-" * 70)
        print("  ACTUAL EVALUATION RESULTS SUMMARY")
        print("-" * 70)
        print(f"  * Sentiment Classification (Logistic Regression vs Majority Baseline):")
        print(f"      - Accuracy:        {sent_metrics['accuracy'] * 100:.2f}%")
        print(f"      - Macro F1-Score:  {sent_metrics['macro_f1']:.4f}")
        print(f"      - Macro Precision: {sent_metrics['macro_precision']:.4f}")
        print(f"      - Macro Recall:    {sent_metrics['macro_recall']:.4f}")
        print(f"  * Content-based Recommender (TF-IDF + Cosine Similarity):")
        print(f"      - Mean Precision@5: {rec_metrics['mean_precision_at_k']:.4f}")
        print(f"      - Mean Recall@5:    {rec_metrics['mean_recall_at_k']:.4f}")
        print(f"      - Mean NDCG@5:      {rec_metrics['mean_ndcg_at_k']:.4f}")
        print(f"      - Catalogue Coverage: {rec_metrics['catalogue_coverage_percentage']:.1f}%")
        print("-" * 70)
        print("\n[SUCCESS] Pipeline completed successfully! Ready to launch web application.\n")
        return 0

    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
