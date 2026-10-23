# GlowRight Project Report: Ingredient-Aware Skincare Recommendations & Customer Review Analytics

## 1. Abstract
E-commerce cosmetics discovery often frustrates consumers due to dense scientific chemical nomenclature (INCI), personal ingredient allergies, and fluctuating customer feedback. This project introduces **GlowRight**, an open, full-stack data science platform combining content-based vector recommendation models with supervised natural language sentiment triage. Utilizing TF-IDF representations, cosine similarity with hard pre-ranking exclusion filters, and class-weighted logistic regression, the application delivers transparent, explainable skincare discovery. Evaluated on reproducible benchmark datasets, the platform achieves robust precision@K, NDCG@K, and multi-class sentiment accuracy without data leakage.

---

## 2. Problem Definition & Business Context
1. **Discovery Friction:** Consumers struggle to parse complex multi-syllabic ingredients to find formulations matching their budget and skin sensitivities.
2. **Review Ambiguity:** Star ratings alone fail to reveal specific cosmetic dissatisfaction (e.g., texture pilling, fragrance sensitivity).
3. **Safety & Transparency:** Black-box recommendation systems often recommend products containing compounds the user explicitly needs to avoid.
4. **Scope & Guardrails:** This system is explicitly an educational and consumer discovery prototype; it does **not** perform medical diagnoses or replace licensed dermatologists.

---

## 3. Data Sources & Provenance
- **Demonstration Dataset:** Curated synthetic benchmark dataset containing 40 representative skincare products and 156 customer reviews.
- **Attributes:** Includes product title, brand, category, retail price, average rating, review count, INCI ingredient list, free-text description, review timestamps, and sentiment annotations.
- **Data Provenance:** All records are flagged with `is_demo=True` and attributed to `Synthetic Internship Benchmark Dataset`.
- **Public Data Ingestion:** Migration pathways for open datasets (Open Beauty Facts under ODbL, Kaggle Sephora) are documented in `data/README.md`.

---

## 4. Data Cleaning & Pipeline Preprocessing
The automated data pipeline (`src/data_pipeline.py`) enforces strict schema validation:
- **Deduplication:** Removes duplicate records based on unique primary keys (`product_id`, `review_id`).
- **Boundary Checks:** Validates price (`0 < price <= 1000`) and customer ratings (`1.0 <= rating <= 5.0`).
- **Text Standardization:** Trims irregular whitespace and standardizes punctuation across ingredient tokens while preserving chemical casing (e.g., *Centella Asiatica*, *L-Ascorbic Acid*).
- **Referential Integrity:** Prunes orphaned customer reviews referencing missing product identifiers.
- **Output Artifacts:** Persists clean datasets to `outputs/cleaned_products.csv` and records cleaning metrics in `outputs/data_summary.json`.

---

## 5. Exploratory Data Analysis (EDA)
Exploratory charts generated via Matplotlib and Seaborn in `src/eda.py`:
1. **Category Depth:** Highlights catalogue concentration across Cleansers, Serums, Moisturizers, Sunscreens, Toners, Exfoliants, Eye Creams, and Masks.
2. **Price Distribution:** Kernel Density Estimation (KDE) plot establishing median retail price points and dispersion.
3. **Rating Distribution:** Box plots displaying customer satisfaction interquartile ranges per category.
4. **Sentiment Class Distribution:** Breakdown of positive, neutral, and negative reviews.
5. **Data Completeness:** Verifies 100% feature completeness post-cleaning.

---

## 6. Feature Engineering & Vector Representations
- **Product Text Fusion:** A consolidated document string is constructed per product:
  $$\text{ContentText}_i = \text{Name}_i \circ \text{Brand}_i \circ \text{Category}_i \circ \text{Description}_i \circ \text{Ingredients}_i$$
- **TF-IDF Vector Space:** Transformed via `TfidfVectorizer(max_features=1500, ngram_range=(1,2), stop_words='english')`.
- **User Query Profile:** The user's free-text query is enriched and weighted with explicitly declared preferred active ingredients.

---

## 7. Model Architecture & Baselines

### 7.1 Content-Based Recommender
- **Constraint Filters (Pre-ranking):**
  - Budget Ceiling: Drop products where $\text{Price} > \text{Budget}_{\max}$.
  - Category Match: Match requested product category (if specified).
  - Hard Exclusion: Drop any product containing any substring present in the user's excluded ingredients list.
- **Ranking Engine:** Cosine Similarity between user query vector $\mathbf{u}$ and candidate product vector $\mathbf{v}_i$:
  $$\text{CosineSimilarity}(\mathbf{u}, \mathbf{v}_i) = \frac{\mathbf{u} \cdot \mathbf{v}_i}{\|\mathbf{u}\|_2 \|\mathbf{v}_i\|_2}$$
- **Baseline Comparison:** Unpersonalized Popularity/Rating baseline ranked by:
  $$\text{Score}_{\text{baseline}} = \text{Rating}_i \times \log_{10}(\text{ReviewCount}_i + 10)$$

### 7.2 Supervised Sentiment Classifier
- **Pipeline:** Fitted strictly on a 75% stratified training partition with sublinear TF-IDF scaling.
- **Primary Model:** Logistic Regression with `class_weight='balanced'` and $C=1.0$.
- **Benchmark Baselines:** Majority-Class Classifier (`DummyClassifier`) and Multinomial Naive Bayes ($α=1.0$).

---

## 8. Empirical Evaluation & Held-out Results

### 8.1 Sentiment Classification (25% Stratified Test Partition)
*(Actual values recorded by `run_pipeline.py`)*
- **Accuracy:** 100.0%
- **Macro F1-Score:** 1.0000
- **Macro Precision:** 1.0000
- **Macro Recall:** 1.0000
- **Baseline Comparison:**
  - Majority Baseline Accuracy: 64.10% (F1: 0.26)
  - Primary Logistic Regression: Outperforms baseline across all classes.

### 8.2 Content Recommender Performance (Benchmark Scenarios, K=5)
- **Mean Precision@5:** 0.3000
- **Mean Recall@5:** 1.0000
- **Mean NDCG@5:** 1.0000
- **Catalogue Coverage:** 57.5% across diverse query topics.

---

## 9. Business Impact & Practical Application
- **Customer Friction Reduction:** Enables users to rapidly locate products matching restrictive ingredient criteria (e.g., fungal acne safe, fragrance-free).
- **Merchandising Intelligence:** Review analytics surface common dissatisfaction themes (e.g., pump leakage, texture heaviness) prior to inventory re-orders.
- **Explainability:** Match reason badges increase consumer trust over opaque deep learning black boxes.

---

## 10. Responsible AI, Safety & Ethical Limitations
- **Prototype Status:** GlowRight is an exploratory decision-support demonstration, not medical advice.
- **No Diagnostic Claims:** The system strictly prohibits condition diagnoses (e.g., eczema, contact dermatitis).
- **Allergy Notice:** Algorithmic similarity does not guarantee personal immunological compatibility. Patch tests remain essential.
- **Ephemeral Input:** User inputs are processed in-memory and are never stored or monetized.

---

## 11. Conclusion & Future Roadmap
GlowRight demonstrates that principled feature engineering, transparent constraint filtering, and leakage-free supervised classification provide a dependable foundation for e-commerce skincare discovery. 
Future expansions include integrating user collaborative filtering signals upon gathering live interaction traffic, incorporating external chemical ontology APIs (e.g., PubChem / CosIng), and deploying containerized microservices.

---

## 12. References
1. Manning, C. D., Raghavan, P., & Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.
2. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
3. European Commission. (2006). *CosIng: Cosmetic Ingredient Database*.
4. Open Beauty Facts Community. (2024). *Open Beauty Facts: The Open Cosmetics Database*.
