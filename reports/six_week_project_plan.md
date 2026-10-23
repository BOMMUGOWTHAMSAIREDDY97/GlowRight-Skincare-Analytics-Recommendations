# GlowRight: Six-Week Internship Project Plan
**Track:** Data Science with Python Analyst Internship  
**Project:** Ingredient-Aware Skincare Recommendations and Customer Review Analytics  
**Author / Intern:** Senior Data Science Intern  
**Academic Period:** 6-Week Curriculum  

---

## Executive Overview
The objective of this project is to develop **GlowRight**, an end-to-end data science application combining content-based filtering for active skincare discovery and supervised natural language processing for customer review sentiment triage. 

This curriculum outlines weekly deliverables, methodology milestones, risk assessments, and evaluation criteria across the six weeks.

```
Week 1: Problem Framing & Scoping ─────────► Week 2: Schema & Provenance
                                                    │
Week 4: EDA & Feature Engineering ◄──────── Week 3: Cleaning & Validation
      │
      ▼
Week 5: Modeling & Baselines ─────────────► Week 6: Held-out Evaluation & Deployment
```

---

## Week-by-Week Breakdown

### Week 1: Problem Definition, Objectives, Scope & Success Criteria
- **Focus:** Domain understanding, stakeholder mapping, and project boundaries.
- **Key Tasks:**
  - Define user personas: Consumer seeking targeted formulations; E-commerce merchant analyzing product sentiment.
  - Determine core capabilities:
    1. Budget-aware and ingredient-aware product matching.
    2. Review sentiment classification and theme extraction.
  - Establish boundary conditions & ethical guidelines:
    - Prototype is an exploratory search tool, **not** clinical dermatological software.
    - No medical diagnosis of conditions (e.g., eczema, acne vulgaris, psoriasis).
    - No guarantees regarding hypoallergenic status or personal immunological safety.
  - Success Criteria:
    - Functional recommendation engine respecting hard exclusions.
    - Supervised sentiment model exceeding a majority-class baseline on held-out test splits.
    - Fully automated data pipeline and test coverage.
- **Deliverables:** Problem statement document, ethics charter, and milestone schedule.

---

### Week 2: Data Sourcing, Schema Design, Data Dictionary & Provenance
- **Focus:** Data architecture and schema standardization.
- **Key Tasks:**
  - Design relational schemas for Products and Reviews.
  - Standardize column definitions: `product_id`, `product_name`, `brand`, `category`, `price`, `rating`, `review_count`, `ingredients`, `description`, `source`, `source_date`, `is_demo`.
  - Design review schema: `review_id`, `product_id`, `rating`, `review_text`, `date`, `sentiment`, `is_demo`.
  - Create curated synthetic benchmark demonstration datasets (`data/products_demo.csv` and `data/reviews_demo.csv`) ensuring zero copyright infringement and zero leakage of proprietary user data.
  - Document migration guidelines for public datasets (Open Beauty Facts, Kaggle Sephora).
- **Deliverables:** `data/README.md` with full Data Dictionary and validation scripts.

---

### Week 3: Data Cleaning, Preprocessing, Validation & Pipeline Automation
- **Focus:** Data quality engineering and reproducible pipelines.
- **Key Tasks:**
  - Build `src/data_pipeline.py`.
  - Implement schema assertion verifying all mandatory fields are present.
  - Handle duplicate primary keys (`product_id`, `review_id`).
  - Validate numeric boundaries:
    - Price: Ensure positive non-zero values (`0 < price <= 1000`).
    - Rating: Ensure bounds within `[1.0, 5.0]`.
  - Clean text fields: Trim whitespace, standardize casing, and normalize ingredient tokens.
  - Enforce referential integrity: Drop orphaned reviews whose `product_id` is absent from products.
  - Save cleaned files to `outputs/cleaned_products.csv` and generate `outputs/data_summary.json`.
- **Deliverables:** Tested automated data ingestion and cleaning pipeline.

---

### Week 4: Exploratory Data Analysis, Feature Engineering & Visualizations
- **Focus:** Statistical discovery and visual reporting.
- **Key Tasks:**
  - Implement `src/eda.py` using Matplotlib and Seaborn with a cohesive brand palette (Sage Green, Terracotta, Warm Cream).
  - Produce publication-ready analytical charts:
    1. Category depth and product counts.
    2. Price distribution with Kernel Density Estimation (KDE) and median overlays.
    3. Rating distributions across product categories via box plots.
    4. Sentiment class breakdown.
    5. Data completeness verification.
  - Extract recurring n-gram keyword themes (bi-grams and tri-grams) from customer reviews.
  - Formulate text representations: Combine product names, categories, descriptions, and INCI ingredient lists into consolidated document vectors.
- **Deliverables:** 5 generated EDA figures in `outputs/` and `web/static/img/eda/`.

---

### Week 5: Algorithm Design, Modeling Pipelines & Benchmark Baselines
- **Focus:** Machine learning modeling for recommendations and sentiment analysis.
- **Key Tasks:**
  - **Recommender (`src/recommender.py`):**
    - Construct TF-IDF Vector Space Matrix across product content texts.
    - Implement pre-ranking constraint filters:
      1. Maximum budget ceiling (`price <= max_budget`).
      2. Category matching.
      3. Hard exclusion filtering (drop products matching excluded ingredient substrings).
    - Compute Cosine Similarity between user query profile and candidate product vectors.
    - Provide human-interpretable match rationales (active ingredients detected, category matches).
    - Build a Popularity/Rating Baseline ranker for objective contrast.
  - **Sentiment Classifier (`src/sentiment.py`):**
    - Implement stratified train/test split (75% train, 25% test).
    - Fit TF-IDF Vectorizer strictly on training data (prevent preprocessing leakage).
    - Train Majority-Class Baseline (`DummyClassifier`) and Multinomial Naive Bayes benchmark.
    - Train class-weighted Logistic Regression as primary classifier.
    - Serialize fitted models safely using `joblib`.
- **Deliverables:** Model artifacts saved in `models/`.

---

### Week 6: Held-out Evaluation, Full-Stack Deployment & Project Report
- **Focus:** Model evaluation, dashboard implementation, and final reporting.
- **Key Tasks:**
  - Implement `src/evaluation.py`:
    - Sentiment metrics: Accuracy, Macro Precision, Macro Recall, Macro F1, Confusion Matrix.
    - Recommender metrics: Mean Precision@5, Mean Recall@5, Mean NDCG@5, and Catalogue Coverage (%).
  - Implement Flask REST API (`app.py`) serving endpoints for health, catalogue, recommendations, reviews, sentiment inference, and evaluation metrics.
  - Build polished single-page interface with responsive cards, live recommendation explorer, and live sentiment sandbox.
  - Implement comprehensive automated test suite with `pytest`.
  - Compile final project report and reproducible repository README.
- **Deliverables:** Completed web application, test report, and final documentation.
