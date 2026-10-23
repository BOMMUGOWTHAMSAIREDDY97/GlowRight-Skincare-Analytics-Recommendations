# GlowRight: Ingredient-Aware Skincare Recommendations & Customer Review Analytics

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/backend-Flask%203.0-green.svg)](https://flask.palletsprojects.com/)
[![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![Tests](https://img.shields.io/badge/tests-22%20passed-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

A full-stack Python data science application developed as a comprehensive **Six-Week Data Science with Python Analyst Internship Project**. 

GlowRight enables consumers to discover skincare formulations tailored to their active ingredient preferences and budget ceilings, provides content-based product recommendations using TF-IDF and Cosine Similarity, extracts customer review themes via NLP n-grams, and runs supervised sentiment classification with held-out validation.

---

## Table of Contents
- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Demonstration Data Notice](#demonstration-data-notice)
- [Installation & Environment Setup](#installation--environment-setup)
- [Running the Data Pipeline](#running-the-data-pipeline)
- [Launching the Web Application](#launching-the-web-application)
- [Automated Testing & Results](#automated-testing--results)
- [REST API Documentation](#rest-api-documentation)
- [Replacing Demo Data with Real Datasets](#replacing-demo-data-with-real-datasets)
- [Git & GitHub Setup Instructions](#git--github-setup-instructions)
- [Responsible AI & Ethical Limitations](#responsible-ai--ethical-limitations)
- [Six-Week Internship Roadmap](#six-week-internship-roadmap)

---

## Key Features

1. **Product Catalogue & Smart Filtering:**
   - Interactive search across product names, brands, categories, descriptions, and INCI ingredient lists.
   - Dynamic price filtering with range sliders, category pills, and multi-field sorting (rating, price, reviews).
   - Detailed modal view displaying full chemical INCI ingredients and verified linked customer reviews.
2. **Ingredient-Aware Personalized Recommendations:**
   - Content-based matching utilizing scikit-learn TF-IDF Vectorizer and Cosine Similarity.
   - **Hard pre-ranking constraints:** Strictly enforces maximum budget limits and drops products containing user-specified excluded ingredients (e.g., *Fragrance*, *Alcohol Denat.*, *Sulfur*).
   - Human-interpretable match badges (e.g., "Contains requested ingredient: Niacinamide", "Aligns with query: soothing").
   - Side-by-side comparison with an unpersonalized Popularity/Rating baseline ranker.
3. **Customer Review Analytics & Skincare Themes:**
   - Sentiment distribution analysis across positive, neutral, and negative customer feedback.
   - Automated extraction of recurring 2-gram and 3-gram skincare themes (e.g., *"sensitive skin"*, *"skin barrier"*, *"lightweight texture"*).
   - Filterable, searchable, and paginated review tables.
4. **Leakage-Free Supervised Sentiment Classification:**
   - Supervised TF-IDF + Logistic Regression pipeline trained with class-balancing and stratified train/test partitions (75% train, 25% test).
   - Zero preprocessing leakage: Vectorizers are fitted strictly on training data.
   - Live interactive sentiment sandbox with class probability breakdown.
5. **Held-Out Model Evaluation Dashboard:**
   - Classification metrics: Accuracy, Macro F1, Precision, Recall, Confusion Matrix, and Majority-Class baseline comparison.
   - Recommendation quality metrics: Precision@K, Recall@K, NDCG@K, and Catalogue Coverage across diverse scenario benchmarks.
   - Publication-quality Exploratory Data Analysis (EDA) charts generated via Matplotlib and Seaborn.

---

## Architecture & Tech Stack

```
GlowRight/
├── app.py                      # Flask Application Server & REST API
├── run_pipeline.py             # Master Pipeline Runner (Ingestion -> Cleaning -> EDA -> ML)
├── requirements.txt            # Dependency declarations
├── .env.example                # Configuration template
├── data/                       # Datasets & Provenance
│   ├── products_demo.csv       # Curated 40-product benchmark catalogue
│   ├── reviews_demo.csv        # Curated 156-review customer feedback dataset
│   └── README.md               # Data dictionary & public dataset migration guide
├── src/                        # Core Data Science & ML Modules
│   ├── config.py               # Paths, constants, schemas, and safety notices
│   ├── data_pipeline.py        # Data validation, cleaning, and text normalization
│   ├── eda.py                  # Matplotlib visual generation
│   ├── recommender.py          # TF-IDF Cosine Similarity & exclusion engine
│   ├── sentiment.py            # Supervised text classification pipeline
│   ├── evaluation.py           # Precision@K, NDCG@K, and held-out validation
│   └── reporting.py            # Review analytics & theme extraction
├── web/                        # Web Presentation Layer
│   ├── templates/index.html    # Single Page Application HTML5 template
│   └── static/
│       ├── css/style.css       # Sage-green & terracotta design system
│       ├── js/app.js           # Client-side SPA controller & API client
│       └── img/eda/            # Generated EDA chart figures
├── outputs/                    # Cleaned CSV outputs & summary JSON
├── models/                     # Serialized joblib artifacts & metrics
├── notebooks/                  # Analytical walkthrough documentation
├── reports/                    # 6-Week project plan & report template
└── tests/                      # Automated pytest suite (22 tests)
```

- **Backend:** Python 3.10+ (tested on Python 3.14.3), Flask 3.0.3, Flask-CORS 4.0.0
- **Data Science & ML:** pandas 3.0.2, NumPy 2.4.4, scikit-learn 1.8.0, SciPy 1.17.1, joblib 1.4.2
- **Data Visualizations:** Matplotlib 3.10.8, Seaborn 0.13.2
- **Testing:** pytest 9.1.1
- **Frontend:** Semantic HTML5, Vanilla CSS3 (Custom Design System), Modern Vanilla JavaScript (ES6+)

---

## Demonstration Data Notice

> [!WARNING]
> **Academic Demonstration Data Notice**
> The files `data/products_demo.csv` and `data/reviews_demo.csv` contain curated synthetic demonstration records created specifically for benchmarking machine learning algorithms and software engineering workflows during a 6-week internship. 
> Values do not represent verified clinical trial outcomes or real commercial brand endorsements. To use real commercial data, follow the [replacement guide](#replacing-demo-data-with-real-datasets).

---

## Installation & Environment Setup

### Prerequisites
- Python 3.10 or newer (Verify using `python --version`)
- Git

### 1. Clone or Open the Workspace
```bash
git clone <your-repository-url>
cd "GlowRight Full-Stack Data Science Project"
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Data Pipeline

Before launching the web server, execute the automated data pipeline to clean the datasets, generate exploratory visualizations, fit the recommendation TF-IDF models, and compute held-out evaluation metrics:

```bash
python run_pipeline.py
```

**Expected Console Output:**
```
======================================================================
  GlowRight: Ingredient-Aware Skincare Recommendation Pipeline
  Internship Data Science with Python Project
======================================================================

[1/3] Running Data Ingestion & Preprocessing Pipeline...
  [+] Cleaned 40 products.
  [+] Cleaned 156 reviews.
  [+] Category counts: {'Serum': 8, 'Moisturizer': 7, 'Cleanser': 5, ...}

[2/3] Generating EDA Visualizations...
  [+] Generated category chart -> eda_category_distribution.png
  [+] Generated price chart -> eda_price_distribution.png
  [+] Generated rating chart -> eda_rating_distribution.png
  [+] Generated sentiment chart -> eda_sentiment_distribution.png
  [+] Generated missingness chart -> eda_missingness.png

[3/3] Training Models & Executing Held-out Evaluation...
----------------------------------------------------------------------
  ACTUAL EVALUATION RESULTS SUMMARY
----------------------------------------------------------------------
  * Sentiment Classification (Logistic Regression vs Majority Baseline):
      - Accuracy:        100.00%
      - Macro F1-Score:  1.0000
      - Macro Precision: 1.0000
      - Macro Recall:    1.0000
  * Content-based Recommender (TF-IDF + Cosine Similarity):
      - Mean Precision@5: 0.3000
      - Mean Recall@5:    1.0000
      - Mean NDCG@5:      1.0000
      - Catalogue Coverage: 57.5%
----------------------------------------------------------------------
[SUCCESS] Pipeline completed successfully! Ready to launch web application.
```

---

## Launching the Web Application

Start the Flask development server:

```bash
python app.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

The application provides a responsive Single Page Application (SPA) with six accessible tabs:
- **Home:** Executive overview, real dataset statistics, and project mission.
- **Catalogue:** Search, filter, and inspect product details and INCI ingredient lists.
- **Recommender:** Content-based recommendation explorer with preferred and excluded ingredient chips.
- **Reviews:** Sentiment breakdown, recurring theme pills, and filterable review tables.
- **Evaluation & ML:** Live sentiment classifier sandbox, confusion matrix, baseline comparison, and EDA gallery.
- **About & Ethics:** Six-week internship progression, data dictionary, and dermatological prototype boundaries.

---

## Automated Testing & Results

GlowRight features comprehensive unit and integration test coverage across data ingestion, recommendation constraints, evaluation calculations, and Flask HTTP routes.

Run the test suite using pytest:
```bash
python -m pytest tests/ -v
```

### Actual Test Results Obtained
```
tests/test_api.py::test_health_endpoint PASSED                           [  4%]
tests/test_api.py::test_summary_endpoint PASSED                          [  9%]
tests/test_api.py::test_products_list_and_filter PASSED                  [ 13%]
tests/test_api.py::test_single_product_details PASSED                    [ 18%]
tests/test_api.py::test_recommendation_api PASSED                        [ 22%]
tests/test_api.py::test_recommendation_invalid_budget PASSED             [ 27%]
tests/test_api.py::test_sentiment_prediction_api PASSED                  [ 31%]
tests/test_api.py::test_evaluation_endpoint PASSED                       [ 36%]
tests/test_data_pipeline.py::test_normalize_ingredient_string PASSED     [ 40%]
tests/test_data_pipeline.py::test_validate_schema_success PASSED         [ 45%]
tests/test_data_pipeline.py::test_validate_schema_failure PASSED         [ 50%]
tests/test_data_pipeline.py::test_clean_products_data_deduplication_and_ranges PASSED [ 54%]
tests/test_data_pipeline.py::test_clean_reviews_data_validation PASSED   [ 59%]
tests/test_evaluation.py::test_sentiment_pipeline_training_and_metrics PASSED [ 63%]
tests/test_evaluation.py::test_sentiment_pipeline_empty_input PASSED     [ 68%]
tests/test_evaluation.py::test_recommender_evaluation_metrics PASSED     [ 72%]
tests/test_recommender.py::test_recommender_hard_exclusion_filter PASSED [ 77%]
tests/test_recommender.py::test_recommender_budget_constraint PASSED     [ 81%]
tests/test_recommender.py::test_recommender_category_filter PASSED       [ 86%]
tests/test_recommender.py::test_recommender_preferred_ingredients_ranking PASSED [ 90%]
tests/test_recommender.py::test_recommender_empty_query_fallback PASSED  [ 95%]
tests/test_recommender.py::test_recommender_no_matching_products PASSED  [100%]

============================= 22 passed in 12.67s =============================
```

---

## REST API Documentation

### 1. System Health
- **`GET /health`**
- **Response:**
  ```json
  {
    "app_name": "GlowRight",
    "initialized": true,
    "models_ready": true,
    "products_count": 40,
    "reviews_count": 156,
    "status": "healthy",
    "version": "1.0.0"
  }
  ```

### 2. Product Catalogue Search & Filter
- **`GET /api/products`**
- **Query Parameters:**
  - `search` (string): Keyword match across title, brand, or ingredients.
  - `category` (string): Filter by product category.
  - `max_price` (float): Maximum price ceiling.
  - `sort_by` (`rating`, `price`, `reviews`, `name`).
  - `sort_dir` (`asc`, `desc`).
  - `page` (int), `per_page` (int).

### 3. Personalized Recommendation Query
- **`POST /api/recommend`**
- **Request Body:**
  ```json
  {
    "query": "soothing barrier repair serum",
    "preferred_ingredients": ["Centella Asiatica", "Ceramide NP"],
    "excluded_ingredients": ["Fragrance"],
    "category": "Serum",
    "max_budget": 35.0,
    "top_k": 3
  }
  ```
- **Response:**
  ```json
  {
    "recommendations": [
      {
        "product_id": "GR-011",
        "product_name": "Centella Calming Relief Ampoule",
        "brand": "PureKare",
        "category": "Serum",
        "price": 19.5,
        "rating": 4.9,
        "review_count": 520,
        "similarity_score": 0.4285,
        "match_reasons": [
          "Contains requested ingredient(s): Centella Asiatica",
          "Matches desired category: Serum",
          "Aligns with query attributes: 'soothing', 'barrier'",
          "Top community rated: 4.9★"
        ]
      }
    ],
    "baseline_popular": [...],
    "metadata": {
      "applied_filters": { "category": "Serum", "max_budget": 35.0 },
      "ranking_method": "TF-IDF Vector Space with Cosine Similarity"
    },
    "disclaimer": "..."
  }
  ```

### 4. Review Sentiment Classification Inference
- **`POST /api/sentiment/predict`**
- **Request Body:**
  ```json
  {
    "review_text": "This oat cleanser completely calmed my sensitive barrier. My holy grail!"
  }
  ```
- **Response:**
  ```json
  {
    "prediction": "positive",
    "confidence": 0.9412,
    "probabilities": {
      "negative": 0.0121,
      "neutral": 0.0467,
      "positive": 0.9412
    },
    "model_used": "TF-IDF + Logistic Regression"
  }
  ```

### 5. Evaluation Metrics
- **`GET /api/evaluation`**
- Returns real held-out metrics for both sentiment classification and recommendation benchmark scenarios.

---

## Replacing Demo Data with Real Datasets

To replace the starter dataset with a legitimate public or licensed dataset:

1. **Recommended Sources:**
   - **Open Beauty Facts:** [world.openbeautyfacts.org](https://world.openbeautyfacts.org/) (ODbL License).
   - **Kaggle Sephora Products & Reviews:** Publicly available research datasets.
2. Ensure columns match the schema defined in [`data/README.md`](data/README.md).
3. Save your transformed files to `data/products_demo.csv` and `data/reviews_demo.csv`.
4. Re-run `python run_pipeline.py` to regenerate all models, charts, and evaluations.

---

## Git & GitHub Setup Instructions

To initialize and push this project to your GitHub portfolio:

```bash
# 1. Initialize git repository
git init

# 2. Add files
git add .

# 3. Create initial commit
git commit -m "feat: complete GlowRight full-stack data science application"

# 4. Set main branch
git branch -M main

# 5. Link to your authentic GitHub repository
# Replace <YOUR-USERNAME> and <YOUR-REPO> with your actual GitHub account details
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO>.git

# 6. Push to remote
git push -u origin main
```

---

## Responsible AI & Ethical Limitations

- **Educational & Prototype Scope:** GlowRight is a data science search tool designed for portfolio demonstration and consumer discovery. It is **not** medical software.
- **No Dermatological Diagnosis:** The system does not diagnose or treat skin pathologies (e.g., eczema, contact dermatitis, rosacea, acne vulgaris).
- **Allergy & Safety Notice:** Text-based ingredient matching does not guarantee personal immunological tolerance. Always perform an allergy patch test and consult a board-certified dermatologist for medical concerns.
- **Review Sentiment Boundary:** Positive customer sentiment indicates personal cosmetic satisfaction and texture preference; it does **not** constitute clinical proof of product efficacy.

---

## Six-Week Internship Roadmap

For the detailed weekly curriculum, milestones, and deliverables, see:
- [`reports/six_week_project_plan.md`](reports/six_week_project_plan.md)
- [`reports/project_report_template.md`](reports/project_report_template.md)
- [`notebooks/analysis_walkthrough.md`](notebooks/analysis_walkthrough.md)
