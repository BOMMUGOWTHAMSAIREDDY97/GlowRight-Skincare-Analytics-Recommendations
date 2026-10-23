# GlowRight: Analysis & Modeling Walkthrough

This document provides a step-by-step analytical walkthrough of the data processing, mathematical formulations, feature engineering, and model evaluation techniques employed in GlowRight.

---

## 1. Data Cleaning & Normalization Pipeline

The raw skincare dataset contains unstructured text, variable formatting, and potential range anomalies.

```python
from src.data_pipeline import clean_products_data, clean_reviews_data
import pandas as pd

raw_products = pd.read_csv("data/products_demo.csv")
cleaned_products, metrics = clean_products_data(raw_products)

print(f"Initial count: {metrics['initial_product_count']}")
print(f"Duplicates removed: {metrics['duplicates_removed']}")
print(f"Final valid count: {metrics['final_product_count']}")
```

### INCI Ingredient Tokenization
Chemical ingredients follow the International Nomenclature of Cosmetic Ingredients (INCI). Punctuation anomalies (semicolons, extra spacing) are normalized to standard comma-separated tokens:
$$\text{CleanedTokens} = \{ \text{trim}(t) \mid t \in \text{split}(T, [',', ';']) \land \text{len}(t) > 0 \}$$

---

## 2. Text Representation & Vectorization

Each product is transformed into a rich textual document combining its title, brand, category, commercial description, and normalized ingredient sequence:

```python
content_text = f"{name} {brand} {category} {description} Ingredients: {ingredients}"
```

### TF-IDF Mathematical Formulation
Term Frequency-Inverse Document Frequency reflects how important a word or n-gram is to a product within the overall catalogue:

$$\text{TF}(t, d) = \frac{f_{t, d}}{\sum_{t' \in d} f_{t', d}}$$

$$\text{IDF}(t, D) = \ln\left( \frac{1 + |D|}{1 + |\{d \in D : t \in d\}|} \right) + 1$$

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

---

## 3. Recommendation Engine: Pre-Ranking & Cosine Similarity

### Step 1: Pre-ranking Constraint Filtering
Before vector ranking occurs, hard negative constraints are applied to guarantee compliance:
1. **Price constraint:** $\text{Price}_i \le \text{MaxBudget}$
2. **Category filter:** $\text{Category}_i = \text{TargetCategory}$
3. **Hard Exclusions:** $\forall e \in \text{ExcludedIngredients}, \neg(e \subseteq \text{Ingredients}_i)$

### Step 2: Cosine Similarity Scoring
For the candidate set $\mathcal{C}$ that survives hard filtering, the cosine similarity between the vectorized user query $\mathbf{u}$ and candidate document vector $\mathbf{v}_i$ is computed:

$$\text{Sim}(\mathbf{u}, \mathbf{v}_i) = \frac{\mathbf{u} \cdot \mathbf{v}_i}{\|\mathbf{u}\|_2 \|\mathbf{v}_i\|_2}$$

### Step 3: Popularity Baseline Contrast
To benchmark against an unpersonalized baseline, products are simultaneously scored using a Bayesian-weighted popularity score:
$$\text{Score}_{\text{pop}} = \text{Rating}_i \times \log_{10}(\text{ReviewCount}_i + 10)$$

---

## 4. Supervised Sentiment Classification (Leakage-Free Pipeline)

```python
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# 1. Stratified Split
X_train, X_test, y_train, y_test = train_test_split(
    reviews['review_text'], reviews['sentiment'],
    test_size=0.25, random_state=42, stratify=reviews['sentiment']
)

# 2. Fit Vectorizer ONLY on X_train (Zero Data Leakage)
vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# 3. Fit Class-Weighted Logistic Regression
clf = LogisticRegression(class_weight='balanced', random_state=42)
clf.fit(X_train_vec, y_train)
```

---

## 5. Held-Out Evaluation Metrics

### 5.1 Recommendation Ranking Metrics
1. **Precision@K:**
   $$\text{Precision@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{K}$$
2. **Recall@K:**
   $$\text{Recall@K} = \frac{|\text{Retrieved}_K \cap \text{Relevant}|}{|\text{Relevant}|}$$
3. **Discounted Cumulative Gain (DCG@K) & NDCG@K:**
   $$\text{DCG@K} = \sum_{r=1}^K \frac{\text{rel}_r}{\log_2(r + 1)}, \quad \text{NDCG@K} = \frac{\text{DCG@K}}{\text{IDCG@K}}$$

---

## 6. Responsible AI & Safety Principles
- Review sentiment reflects personal user experience and does not prove clinical therapeutic effectiveness.
- Recommendations represent statistical text alignment, not medical or allergy tolerance certification.
