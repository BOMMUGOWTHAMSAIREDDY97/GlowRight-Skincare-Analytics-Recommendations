# GlowRight Data Directory & Provenance Documentation

## Overview

This directory houses the product catalogue and customer review datasets utilized by GlowRight. 
By default, this repository provides **curated synthetic benchmark demonstration data** (`products_demo.csv` and `reviews_demo.csv`) to enable an out-of-the-box working data science application without committing proprietary or unverified user data.

> [!WARNING]
> **Synthetic Demonstration Data Notice**
> The files `products_demo.csv` and `reviews_demo.csv` are synthetically generated for academic evaluation and software development testing during a 6-week internship project. They do **not** represent verified clinical safety records, real commercial brand endorsements, or real customer identities.

---

## Data Dictionary

### 1. Products Catalogue (`products_demo.csv`)

| Column Name | Data Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `product_id` | String | Unique, Required | Unique identifier for product | `GR-001` |
| `product_name` | String | Required | Full title of the skincare product | `Gentle Hydrating Oat Cleanser` |
| `brand` | String | Required | Brand or manufacturer name | `Aura Botanica` |
| `category` | String | Enum, Required | Cleanser, Serum, Moisturizer, Sunscreen, Toner, Exfoliant, Eye Cream, Mask | `Cleanser` |
| `price` | Float | `>= 0.0` | Retail price in USD | `16.50` |
| `rating` | Float | `1.0 <= x <= 5.0` | Average customer rating out of 5.0 | `4.7` |
| `review_count`| Integer | `>= 0` | Total number of recorded reviews | `342` |
| `ingredients` | String | Required | Comma-separated list of cosmetic ingredients (INCI standard) | `Aqua, Oat Kernel Extract, Glycerin...` |
| `description` | String | Required | Commercial product description and application details | `A soothing, non-foaming daily cream cleanser...` |
| `source` | String | Optional | Source provenance indicator | `Synthetic Internship Benchmark Dataset` |
| `source_date` | String (ISO)| Optional | Date of record creation/extraction (YYYY-MM-DD) | `2026-03-01` |
| `is_demo` | Boolean | Required | Boolean flag indicating whether the record is synthetic demo data | `True` |

---

### 2. Customer Reviews (`reviews_demo.csv`)

| Column Name | Data Type | Constraint | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `review_id` | String | Unique, Required | Unique review transaction ID | `REV-0001` |
| `product_id` | String | Foreign Key | References `products_demo.csv(product_id)` | `GR-001` |
| `rating` | Float | `1.0 <= x <= 5.0` | Customer-assigned star rating | `5.0` |
| `review_text` | String | Required | Free-form textual review submitted by the customer | `Absolutely love this cleanser. The oat makes an immediate difference...` |
| `date` | String (ISO)| Optional | Submission date (YYYY-MM-DD) | `2026-02-14` |
| `sentiment` | String | Enum (`positive`, `neutral`, `negative`) | Validated or weakly-labeled sentiment target | `positive` |
| `is_demo` | Boolean | Required | Boolean flag indicating whether the record is synthetic demo data | `True` |

---

## Instructions: Replacing with Real Public Datasets

To replace the synthetic demonstration data with a legitimate public or licensed dataset:

### Recommended Public Datasets
1. **Open Beauty Facts (Opendata)**:
   - Source: [Open Beauty Facts](https://world.openbeautyfacts.org/)
   - License: Open Database License (ODbL)
   - Scope: Crowdsourced global cosmetics data with INCI ingredient lists and categories.
2. **Kaggle Sephora Skincare Products and Reviews**:
   - Source: Kaggle (Public Datasets under CC BY-SA or Open Data Commons)
   - Scope: Real product attributes, brand names, ratings, and customer reviews.

### Replacement Steps
1. Ensure the dataset licence permits non-commercial academic research and storage.
2. Anonymize any personal user identifiers (emails, usernames, IP addresses).
3. Transform the columns to match the required schema defined above.
4. Place the transformed files as:
   - `data/products_demo.csv` (or configure path in `src/config.py`)
   - `data/reviews_demo.csv`
5. Set `is_demo=False` and update the `source` and `source_date` columns accordingly.
6. Run the automated data cleaning and validation pipeline:
   ```bash
   python run_pipeline.py
   ```
7. Verify schema integrity and review the updated metrics generated in `outputs/data_summary.json`.
