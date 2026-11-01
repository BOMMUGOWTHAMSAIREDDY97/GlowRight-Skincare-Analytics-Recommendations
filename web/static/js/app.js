/**
 * GlowRight: Frontend Client Application
 * Handles SPA navigation, catalogue filtering, recommendation queries,
 * review analytics, live sentiment inference, and evaluation dashboards.
 */

const STATE = {
  activeTab: "home",
  summary: null,
  categories: [],
  catalogue: {
    search: "",
    category: "",
    max_price: null,
    sort_by: "rating",
    sort_dir: "desc",
    page: 1,
    per_page: 9,
    total_pages: 1,
  },
  recommender: {
    preferred: ["Niacinamide", "Centella Asiatica"],
    excluded: ["Fragrance"],
    category: "",
    max_budget: 35,
    top_k: 5,
  },
  reviews: {
    product_id: "",
    sentiment: "",
    min_rating: "",
    search: "",
    page: 1,
    per_page: 10,
  },
};

// -----------------------------------------------------------------------------
// DOM Ready & Navigation
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  initHomeView();
  initCatalogueView();
  initRecommenderView();
  initReviewsView();
  initEvaluationView();

  // Load initial global data
  fetchSummaryData();
  fetchCategories();
});

function initNavigation() {
  const navButtons = document.querySelectorAll(".nav-btn");
  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      switchTab(tabId);
    });
  });
}

function switchTab(tabId) {
  STATE.activeTab = tabId;

  // Update Nav Buttons
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update View Sections
  document.querySelectorAll(".view-section").forEach((sec) => {
    if (sec.id === `view-${tabId}`) {
      sec.classList.add("active");
    } else {
      sec.classList.remove("active");
    }
  });

  // Lazy trigger view-specific loaders
  if (tabId === "catalogue") {
    loadProducts();
  } else if (tabId === "reviews") {
    loadReviews();
  } else if (tabId === "evaluation") {
    loadEvaluationData();
  }
}

// -----------------------------------------------------------------------------
// View 1: Home Overview & Global Summary
// -----------------------------------------------------------------------------
function initHomeView() {
  document.querySelectorAll("[data-action='jump-rec']").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("recommender");
    });
  });
  document.querySelectorAll("[data-action='jump-catalogue']").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      switchTab("catalogue");
    });
  });
}

async function fetchSummaryData() {
  try {
    const res = await fetch("/api/summary");
    if (!res.ok) throw new Error("Failed to fetch summary.");
    const data = await res.json();
    STATE.summary = data;

    // Render Stats
    document.getElementById("stat-products").textContent = data.catalogue.total_products;
    document.getElementById("stat-reviews").textContent = data.catalogue.total_reviews;
    document.getElementById("stat-avg-price").textContent = `$${data.catalogue.average_price.toFixed(2)}`;
    document.getElementById("stat-avg-rating").textContent = `${data.catalogue.average_rating.toFixed(1)} ★`;
    document.getElementById("stat-brands").textContent = data.catalogue.total_brands;
  } catch (err) {
    console.error("Summary error:", err);
  }
}

async function fetchCategories() {
  try {
    const res = await fetch("/api/categories");
    if (!res.ok) throw new Error("Failed to load categories.");
    const data = await res.json();
    STATE.categories = data.categories;

    renderCatalogueCategoryPills();
    populateCategoryDropdowns();
  } catch (err) {
    console.error("Categories fetch error:", err);
  }
}

function renderCatalogueCategoryPills() {
  const container = document.getElementById("catalogue-category-pills");
  if (!container) return;

  container.innerHTML = `
    <button class="pill-btn ${STATE.catalogue.category === "" ? "active" : ""}" data-cat="">All Categories</button>
  `;

  STATE.categories.forEach((c) => {
    const catSlug = c.name.toLowerCase().replace(/[^a-z0-9]/g, "-");
    const btn = document.createElement("button");
    btn.className = `pill-btn cat-pill-${catSlug} ${STATE.catalogue.category === c.name ? "active" : ""}`;
    btn.setAttribute("data-cat", c.name);
    btn.textContent = `${c.name} (${c.count})`;
    btn.addEventListener("click", () => {
      STATE.catalogue.category = c.name;
      STATE.catalogue.page = 1;
      updateActivePill(container, btn);
      loadProducts();
    });
    container.appendChild(btn);
  });

  container.querySelector("[data-cat='']").addEventListener("click", (e) => {
    STATE.catalogue.category = "";
    STATE.catalogue.page = 1;
    updateActivePill(container, e.target);
    loadProducts();
  });
}

function updateActivePill(container, activeBtn) {
  container.querySelectorAll(".pill-btn").forEach((b) => b.classList.remove("active"));
  activeBtn.classList.add("active");
}

function populateCategoryDropdowns() {
  const recSelect = document.getElementById("rec-category-select");
  if (recSelect) {
    recSelect.innerHTML = `<option value="">All Categories</option>`;
    STATE.categories.forEach((c) => {
      recSelect.innerHTML += `<option value="${c.name}">${c.name}</option>`;
    });
  }
}

// -----------------------------------------------------------------------------
// View 2: Product Catalogue
// -----------------------------------------------------------------------------
function initCatalogueView() {
  const searchInput = document.getElementById("catalogue-search-input");
  const priceSlider = document.getElementById("catalogue-price-slider");
  const priceDisplay = document.getElementById("catalogue-price-display");
  const sortSelect = document.getElementById("catalogue-sort-select");

  let debounceTimer;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      STATE.catalogue.search = e.target.value.trim();
      STATE.catalogue.page = 1;
      loadProducts();
    }, 280);
  });

  priceSlider.addEventListener("input", (e) => {
    const val = parseFloat(e.target.value);
    priceDisplay.textContent = `$${val}`;
  });

  priceSlider.addEventListener("change", (e) => {
    STATE.catalogue.max_price = parseFloat(e.target.value);
    STATE.catalogue.page = 1;
    loadProducts();
  });

  sortSelect.addEventListener("change", (e) => {
    const [by, dir] = e.target.value.split(":");
    STATE.catalogue.sort_by = by;
    STATE.catalogue.sort_dir = dir;
    STATE.catalogue.page = 1;
    loadProducts();
  });

  document.getElementById("catalogue-prev-page").addEventListener("click", () => {
    if (STATE.catalogue.page > 1) {
      STATE.catalogue.page--;
      loadProducts();
    }
  });

  document.getElementById("catalogue-next-page").addEventListener("click", () => {
    if (STATE.catalogue.page < STATE.catalogue.total_pages) {
      STATE.catalogue.page++;
      loadProducts();
    }
  });
}

async function loadProducts() {
  const grid = document.getElementById("products-grid");
  grid.innerHTML = `<div class="empty-state"><p>Loading catalogue items...</p></div>`;

  const params = new URLSearchParams({
    page: STATE.catalogue.page,
    per_page: STATE.catalogue.per_page,
    sort_by: STATE.catalogue.sort_by,
    sort_dir: STATE.catalogue.sort_dir,
  });

  if (STATE.catalogue.search) params.append("search", STATE.catalogue.search);
  if (STATE.catalogue.category) params.append("category", STATE.catalogue.category);
  if (STATE.catalogue.max_price) params.append("max_price", STATE.catalogue.max_price);

  try {
    const res = await fetch(`/api/products?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to load products.");
    const data = await res.json();

    STATE.catalogue.total_pages = data.pagination.total_pages;
    document.getElementById("catalogue-page-info").textContent = `Page ${data.pagination.page} of ${data.pagination.total_pages} (${data.pagination.total_records} products)`;

    document.getElementById("catalogue-prev-page").disabled = data.pagination.page <= 1;
    document.getElementById("catalogue-next-page").disabled = data.pagination.page >= data.pagination.total_pages;

    if (!data.products || data.products.length === 0) {
      grid.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
          <div class="empty-icon">🍃</div>
          <h3 class="empty-title">No products match your filters</h3>
          <p class="empty-desc">Try clearing your search term, adjusting maximum price, or selecting a broader category.</p>
          <button class="btn btn-secondary btn-sm" onclick="resetCatalogueFilters()">Reset Filters</button>
        </div>
      `;
      return;
    }

    grid.innerHTML = "";
    data.products.forEach((p) => {
      grid.appendChild(createProductCard(p));
    });
  } catch (err) {
    grid.innerHTML = `<div class="empty-state" style="grid-column: 1/-1;"><p>Failed to load products: ${err.message}</p></div>`;
  }
}

function resetCatalogueFilters() {
  document.getElementById("catalogue-search-input").value = "";
  document.getElementById("catalogue-price-slider").value = 75;
  document.getElementById("catalogue-price-display").textContent = "$75";
  STATE.catalogue.search = "";
  STATE.catalogue.category = "";
  STATE.catalogue.max_price = 75;
  STATE.catalogue.page = 1;
  renderCatalogueCategoryPills();
  loadProducts();
}

function createProductCard(p) {
  const catSlug = (p.category || "").toLowerCase().replace(/[^a-z0-9]/g, "-");
  const card = document.createElement("div");
  card.className = `product-card card-cat-${catSlug}`;

  // Shorten ingredients preview
  const ingShort = (p.ingredients_normalized || p.ingredients || "").slice(0, 85) + "...";

  card.innerHTML = `
    <div class="product-card-top">
      <div class="product-badges">
        <span class="badge-cat cat-badge-${catSlug}">${p.category}</span>
        ${p.is_demo ? `<span class="badge-demo">Demo Data</span>` : ""}
      </div>
      <div class="product-brand">${p.brand}</div>
      <h3 class="product-title">${p.product_name}</h3>
      <p class="product-desc">${p.description}</p>
      <div class="product-rating">
        <span class="stars">★</span> ${p.rating.toFixed(1)}
        <span class="rating-count">(${p.review_count} reviews)</span>
      </div>
      <div class="product-ingredients-preview">
        <strong>INCI:</strong> ${ingShort}
      </div>
    </div>
    <div class="product-card-bottom">
      <span class="product-price">$${p.price.toFixed(2)}</span>
      <button class="btn btn-secondary btn-sm" onclick="openProductModal('${p.product_id}')">
        Inspect Details
      </button>
    </div>
  `;
  return card;
}

// -----------------------------------------------------------------------------
// Product Detail Modal
// -----------------------------------------------------------------------------
async function openProductModal(productId) {
  const modal = document.getElementById("product-detail-modal");
  const body = document.getElementById("modal-body-content");
  modal.classList.add("active");
  body.innerHTML = `<p>Loading product details...</p>`;

  try {
    const res = await fetch(`/api/products/${productId}`);
    if (!res.ok) throw new Error("Product not found.");
    const data = await res.json();
    const p = data.product;
    const revs = data.reviews || [];

    let reviewsHtml = revs
      .map(
        (r) => `
        <div style="padding: 0.8rem 0; border-bottom: 1px solid var(--color-beige-border);">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <div>
              <span class="stars">★</span> <strong>${r.rating.toFixed(1)}</strong>
              <span style="font-size: 0.78rem; color: var(--color-text-light); margin-left: 0.5rem;">${r.date}</span>
            </div>
            <span class="sentiment-badge ${r.sentiment}">${r.sentiment}</span>
          </div>
          <p style="font-size: 0.88rem; color: var(--color-text-main);">${r.review_text}</p>
        </div>
      `
      )
      .join("");

    if (!reviewsHtml) {
      reviewsHtml = `<p style="font-size: 0.85rem; color: var(--color-text-muted);">No reviews recorded yet for this demo product.</p>`;
    }

    body.innerHTML = `
      <div class="product-badges" style="margin-bottom: 0.4rem;">
        <span class="badge-cat">${p.category}</span>
        <span class="badge-demo">Demo Benchmark Item</span>
      </div>
      <div style="font-size: 0.82rem; text-transform: uppercase; color: var(--color-text-light); font-weight: 600;">
        ${p.brand} &bull; ${p.product_id}
      </div>
      <h2 style="font-family: var(--font-serif); font-size: 1.6rem; color: var(--color-primary-dark); margin: 0.3rem 0 0.8rem;">
        ${p.product_name}
      </h2>
      <div style="display: flex; gap: 1.5rem; align-items: baseline; margin-bottom: 1rem;">
        <span style="font-family: var(--font-serif); font-size: 1.8rem; font-weight: 700; color: var(--color-primary-dark);">
          $${p.price.toFixed(2)}
        </span>
        <span style="font-size: 0.95rem; font-weight: 600;">
          <span class="stars">★</span> ${p.rating.toFixed(1)} (${p.review_count} community reviews)
        </span>
      </div>
      <p style="font-size: 0.92rem; line-height: 1.6; color: var(--color-text-main); margin-bottom: 1.2rem;">
        ${p.description}
      </p>

      <div style="background: var(--color-cream); padding: 1rem; border-radius: var(--radius-sm); border: 1px solid var(--color-beige-border); margin-bottom: 1.5rem;">
        <h4 style="font-size: 0.84rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--color-primary-dark); margin-bottom: 0.4rem;">
          Complete INCI Ingredient List
        </h4>
        <p style="font-size: 0.82rem; color: var(--color-text-muted); line-height: 1.5;">
          ${p.ingredients_normalized || p.ingredients}
        </p>
      </div>

      <div class="alert-box" style="margin: 1rem 0;">
        <div class="alert-title">Dermatological Prototype Notice</div>
        Ingredient lists are parsed for algorithmic content similarity matching and do not substitute for formal allergy patch tests or professional medical supervision.
      </div>

      <h3 style="font-family: var(--font-serif); font-size: 1.2rem; color: var(--color-primary-dark); margin: 1.5rem 0 0.8rem;">
        Customer Reviews (${revs.length})
      </h3>
      <div style="max-height: 250px; overflow-y: auto;">
        ${reviewsHtml}
      </div>
    `;
  } catch (err) {
    body.innerHTML = `<p>Error loading product details: ${err.message}</p>`;
  }
}

function closeProductModal() {
  document.getElementById("product-detail-modal").classList.remove("active");
}

// -----------------------------------------------------------------------------
// View 3: Personalized Recommendations
// -----------------------------------------------------------------------------
function initRecommenderView() {
  renderChips("preferred");
  renderChips("excluded");

  // Prompt suggestions
  document.querySelectorAll("[data-rec-query]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("rec-query-input").value = btn.getAttribute("data-rec-query");
    });
  });

  // Suggestion chips
  document.querySelectorAll("[data-add-pref]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const ing = btn.getAttribute("data-add-pref");
      if (!STATE.recommender.preferred.includes(ing)) {
        STATE.recommender.preferred.push(ing);
        renderChips("preferred");
      }
    });
  });

  document.querySelectorAll("[data-add-excl]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const ing = btn.getAttribute("data-add-excl");
      if (!STATE.recommender.excluded.includes(ing)) {
        STATE.recommender.excluded.push(ing);
        renderChips("excluded");
      }
    });
  });

  // Budget slider
  const budgetSlider = document.getElementById("rec-budget-slider");
  const budgetDisplay = document.getElementById("rec-budget-display");
  budgetSlider.addEventListener("input", (e) => {
    budgetDisplay.textContent = `$${e.target.value}`;
  });

  // Submit button
  document.getElementById("rec-submit-btn").addEventListener("click", runRecommendationSearch);

  // Chip input handlers
  setupChipTextInput("preferred-text-input", "preferred");
  setupChipTextInput("excluded-text-input", "excluded");
}

function setupChipTextInput(inputId, type) {
  const input = document.getElementById(inputId);
  if (!input) return;

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      const val = input.value.trim().replace(/,/g, "");
      if (val && !STATE.recommender[type].includes(val)) {
        STATE.recommender[type].push(val);
        input.value = "";
        renderChips(type);
      }
    }
  });
}

function renderChips(type) {
  const container = document.getElementById(`${type}-chips-container`);
  const textInput = document.getElementById(`${type}-text-input`);
  if (!container || !textInput) return;

  // Clear existing chips but keep input
  container.querySelectorAll(".chip").forEach((c) => c.remove());

  STATE.recommender[type].forEach((ing) => {
    const chip = document.createElement("span");
    chip.className = `chip ${type === "excluded" ? "chip-excluded" : ""}`;
    chip.innerHTML = `
      ${ing}
      <button class="chip-remove" onclick="removeChip('${type}', '${ing}')">&times;</button>
    `;
    container.insertBefore(chip, textInput);
  });
}

function removeChip(type, ing) {
  STATE.recommender[type] = STATE.recommender[type].filter((item) => item !== ing);
  renderChips(type);
}

async function runRecommendationSearch() {
  const query = document.getElementById("rec-query-input").value.trim();
  const category = document.getElementById("rec-category-select").value;
  const budget = parseFloat(document.getElementById("rec-budget-slider").value);
  const topK = parseInt(document.getElementById("rec-topk-select").value, 10);

  const resultsPanel = document.getElementById("rec-results-panel");
  resultsPanel.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">⏳</div>
      <h3 class="empty-title">Analyzing Ingredient Profiles...</h3>
      <p class="empty-desc">Computing TF-IDF vector projections, applying hard ingredient exclusions, and calculating cosine similarities.</p>
    </div>
  `;

  try {
    const payload = {
      query: query,
      preferred_ingredients: STATE.recommender.preferred,
      excluded_ingredients: STATE.recommender.excluded,
      category: category,
      max_budget: budget,
      top_k: topK,
    };

    const res = await fetch("/api/recommend", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error("Recommendation failed.");
    const data = await res.json();
    renderRecommendationResults(data);
  } catch (err) {
    resultsPanel.innerHTML = `
      <div class="empty-state">
        <p>Error computing recommendations: ${err.message}</p>
      </div>
    `;
  }
}

function renderRecommendationResults(data) {
  const panel = document.getElementById("rec-results-panel");
  const recs = data.recommendations || [];
  const baseline = data.baseline_popular || [];
  const meta = data.metadata || {};

  if (recs.length === 0) {
    panel.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🍃</div>
        <h3 class="empty-title">No Products Matched Your Criteria</h3>
        <p class="empty-desc">${meta.message || "Try relaxing your budget ceiling or removing excluded ingredients."}</p>
      </div>
    `;
    return;
  }

  let html = `
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1rem;">
      <h3 style="font-family: var(--font-serif); font-size: 1.5rem; color: var(--color-primary-dark);">
        Personalized Matches (${recs.length} products)
      </h3>
      <span style="font-size: 0.8rem; color: var(--color-text-light);">
        Filtered from ${meta.total_catalogue} catalogue products
      </span>
    </div>
  `;

  recs.forEach((r, idx) => {
    const catSlug = (r.category || "").toLowerCase().replace(/[^a-z0-9]/g, "-");
    const simPct = (r.similarity_score * 100).toFixed(1);
    const reasonsHtml = (r.match_reasons || [])
      .map((m) => `<span class="reason-tag">✓ ${m}</span>`)
      .join("");

    html += `
      <div class="rec-card card-cat-${catSlug}">
        <div>
          <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.3rem;">
            <span class="badge-cat cat-badge-${catSlug}">${r.category}</span>
            <span style="font-size: 0.78rem; text-transform: uppercase; color: var(--color-text-light); font-weight: 700;">
              ${r.brand}
            </span>
          </div>
          <h4 style="font-family: var(--font-serif); font-size: 1.25rem; font-weight: 700; color: var(--color-primary-dark); margin-bottom: 0.4rem;">
            #${idx + 1}. ${r.product_name}
          </h4>
          <p style="font-size: 0.88rem; color: var(--color-text-muted); margin-bottom: 0.6rem;">
            ${r.description || ""}
          </p>
          <div class="rec-reasons">${reasonsHtml}</div>
          <div style="display: flex; gap: 1rem; align-items: center; font-size: 0.85rem; font-weight: 600;">
            <span class="product-price">$${r.price.toFixed(2)}</span>
            <span><span class="stars">★</span> ${r.rating.toFixed(1)} (${r.review_count} reviews)</span>
          </div>
        </div>
        <div class="rec-score-box">
          <span class="rec-score-val">${simPct}%</span>
          <span class="rec-score-lbl">Match Score</span>
        </div>
      </div>
    `;
  });

  // Baseline Comparison Section
  html += `
    <div style="margin-top: 2.5rem; padding-top: 2rem; border-top: 1px dashed var(--color-beige-border);">
      <div style="margin-bottom: 1rem;">
        <span class="section-tag">Baseline Benchmark Comparison</span>
        <h4 style="font-family: var(--font-serif); font-size: 1.3rem; color: var(--color-primary-dark);">
          Popularity / Customer Rating Baseline
        </h4>
        <p style="font-size: 0.82rem; color: var(--color-text-muted);">
          Compare our content-based personalized match with the standard unpersonalized popularity baseline (ranked strictly by weighted customer rating).
        </p>
      </div>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem;">
  `;

  baseline.forEach((b) => {
    html += `
      <div style="background: linear-gradient(135deg, #f8faff 0%, #fef6ff 100%); border: 1.5px solid var(--color-border); border-radius: var(--radius-md); padding: 1.2rem; box-shadow: var(--shadow-sm);">
        <span style="font-size: 0.72rem; font-weight: 800; text-transform: uppercase; background: var(--grad-aurora); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">${b.category}</span>
        <h5 style="font-size: 1rem; font-weight: 800; color: var(--color-text-main); margin: 0.3rem 0;">${b.product_name}</h5>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700; margin-top: 0.6rem;">
          <span style="color: var(--color-primary-dark); font-size: 1.1rem;">$${b.price.toFixed(2)}</span>
          <span><span class="stars">★</span> ${b.rating.toFixed(1)}</span>
        </div>
      </div>
    `;
  });

  html += `</div></div>`;
  panel.innerHTML = html;
}

// -----------------------------------------------------------------------------
// View 4: Customer Review Analytics
// -----------------------------------------------------------------------------
function initReviewsView() {
  const sentimentFilter = document.getElementById("review-sentiment-filter");
  const searchInput = document.getElementById("review-search-input");

  sentimentFilter.addEventListener("change", (e) => {
    STATE.reviews.sentiment = e.target.value;
    STATE.reviews.page = 1;
    loadReviews();
  });

  let debounceTimer;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      STATE.reviews.search = e.target.value.trim();
      STATE.reviews.page = 1;
      loadReviews();
    }, 300);
  });

  document.getElementById("review-prev-page").addEventListener("click", () => {
    if (STATE.reviews.page > 1) {
      STATE.reviews.page--;
      loadReviews();
    }
  });

  document.getElementById("review-next-page").addEventListener("click", () => {
    if (STATE.reviews.page < STATE.reviews.total_pages) {
      STATE.reviews.page++;
      loadReviews();
    }
  });
}

async function loadReviews() {
  const tbody = document.getElementById("reviews-table-body");
  tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">Loading reviews...</td></tr>`;

  const params = new URLSearchParams({
    page: STATE.reviews.page,
    per_page: STATE.reviews.per_page,
  });

  if (STATE.reviews.sentiment) params.append("sentiment", STATE.reviews.sentiment);
  if (STATE.reviews.search) params.append("search", STATE.reviews.search);

  try {
    const res = await fetch(`/api/reviews?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to load reviews.");
    const data = await res.json();

    STATE.reviews.total_pages = data.pagination.total_pages;
    document.getElementById("reviews-page-info").textContent = `Page ${data.pagination.page} of ${data.pagination.total_pages} (${data.pagination.total_records} reviews)`;

    document.getElementById("review-prev-page").disabled = data.pagination.page <= 1;
    document.getElementById("review-next-page").disabled = data.pagination.page >= data.pagination.total_pages;

    // Render Recurring Themes
    renderRecurringThemes(data.summary.recurring_themes || []);

    // Render Review Rows
    if (!data.reviews || data.reviews.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 2rem;">No customer reviews match your search.</td></tr>`;
      return;
    }

    tbody.innerHTML = data.reviews
      .map(
        (r) => `
        <tr>
          <td style="font-family: monospace; font-size: 0.8rem; font-weight: 600;">${r.review_id}</td>
          <td><strong>${r.product_id}</strong></td>
          <td><span class="stars">★</span> ${r.rating.toFixed(1)}</td>
          <td><span class="sentiment-badge ${r.sentiment}">${r.sentiment}</span></td>
          <td style="max-width: 480px;">${r.review_text}</td>
        </tr>
      `
      )
      .join("");
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Error: ${err.message}</td></tr>`;
  }
}

function renderRecurringThemes(themes) {
  const grid = document.getElementById("recurring-themes-grid");
  if (!grid) return;

  grid.innerHTML = themes
    .map(
      (t) => `
      <div class="theme-pill">
        <span class="theme-title">"${t.theme}"</span>
        <span class="theme-count">${t.occurrences} mentions</span>
      </div>
    `
    )
    .join("");
}

// -----------------------------------------------------------------------------
// View 5: Model Evaluation & Sentiment Classifier Sandbox
// -----------------------------------------------------------------------------
function initEvaluationView() {
  // Live prediction test button
  document.getElementById("sentiment-predict-btn").addEventListener("click", runLiveSentimentPrediction);

  // Example review buttons
  document.querySelectorAll("[data-sample-review]").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.getElementById("sentiment-test-input").value = btn.getAttribute("data-sample-review");
    });
  });
}

async function runLiveSentimentPrediction() {
  const text = document.getElementById("sentiment-test-input").value.trim();
  const resultBox = document.getElementById("sentiment-result-box");

  if (!text) {
    alert("Please enter a customer review text to test.");
    return;
  }

  resultBox.style.display = "block";
  resultBox.innerHTML = "<p>Running inference with trained TF-IDF + Logistic Regression pipeline...</p>";

  try {
    const res = await fetch("/api/sentiment/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ review_text: text }),
    });

    if (!res.ok) throw new Error("Inference failed.");
    const data = await res.json();

    const probs = data.probabilities || {};
    const posPct = ((probs.positive || 0) * 100).toFixed(1);
    const neuPct = ((probs.neutral || 0) * 100).toFixed(1);
    const negPct = ((probs.negative || 0) * 100).toFixed(1);

    resultBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <div>
          <span style="font-size: 0.75rem; text-transform: uppercase; color: var(--color-text-light); font-weight: 700;">
            Predicted Class
          </span>
          <div style="font-family: var(--font-serif); font-size: 1.4rem; font-weight: 700; color: var(--color-primary-dark); text-transform: capitalize;">
            <span class="sentiment-badge ${data.prediction}" style="font-size: 0.95rem;">${data.prediction}</span>
          </div>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 0.75rem; text-transform: uppercase; color: var(--color-text-light); font-weight: 700;">
            Confidence
          </span>
          <div style="font-size: 1.3rem; font-weight: 700; color: var(--color-primary);">
            ${(data.confidence * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      <div style="margin-top: 1rem;">
        <div class="prob-bar-row">
          <span class="prob-label">Positive</span>
          <div class="prob-track"><div class="prob-fill positive" style="width: ${posPct}%;"></div></div>
          <span class="prob-val">${posPct}%</span>
        </div>
        <div class="prob-bar-row">
          <span class="prob-label">Neutral</span>
          <div class="prob-track"><div class="prob-fill neutral" style="width: ${neuPct}%;"></div></div>
          <span class="prob-val">${neuPct}%</span>
        </div>
        <div class="prob-bar-row">
          <span class="prob-label">Negative</span>
          <div class="prob-track"><div class="prob-fill negative" style="width: ${negPct}%;"></div></div>
          <span class="prob-val">${negPct}%</span>
        </div>
      </div>

      <div style="margin-top: 1rem; font-size: 0.75rem; color: var(--color-text-light); text-align: right;">
        Model: ${data.model_used} &bull; Stratified held-out trained
      </div>
    `;
  } catch (err) {
    resultBox.innerHTML = `<p style="color: red;">Error during prediction: ${err.message}</p>`;
  }
}

async function loadEvaluationData() {
  try {
    const res = await fetch("/api/evaluation");
    if (!res.ok) throw new Error("Evaluation metrics unavailable.");
    const data = await res.json();

    if (data.status === "not_evaluated_yet") {
      document.getElementById("eval-status-banner").style.display = "block";
      return;
    }

    // Render Classification Metrics
    const sMetrics = data.sentiment_classification.metrics;
    document.getElementById("eval-acc").textContent = `${(sMetrics.accuracy * 100).toFixed(1)}%`;
    document.getElementById("eval-f1").textContent = sMetrics.macro_f1.toFixed(4);
    document.getElementById("eval-prec").textContent = sMetrics.macro_precision.toFixed(4);
    document.getElementById("eval-rec").textContent = sMetrics.macro_recall.toFixed(4);

    // Confusion Matrix Table
    renderConfusionMatrix(data.sentiment_classification.confusion_matrix);

    // Baseline Model Comparison Table
    renderBaselineTable(data.sentiment_classification.baseline_comparison);

    // Recommender Metrics
    const rMetrics = data.content_recommender;
    document.getElementById("eval-p-k").textContent = rMetrics.mean_precision_at_k.toFixed(4);
    document.getElementById("eval-r-k").textContent = rMetrics.mean_recall_at_k.toFixed(4);
    document.getElementById("eval-ndcg").textContent = rMetrics.mean_ndcg_at_k.toFixed(4);
    document.getElementById("eval-cov").textContent = `${rMetrics.catalogue_coverage_percentage}%`;

    // Recommender Scenarios Table
    renderScenarioTable(rMetrics.scenario_details);

    // Load EDA Charts
    loadEDACharts();
  } catch (err) {
    console.error("Evaluation loading error:", err);
  }
}

function renderConfusionMatrix(cm) {
  const container = document.getElementById("confusion-matrix-container");
  if (!container || !cm) return;

  const labels = cm.labels;
  const matrix = cm.matrix;

  let html = `
    <table class="data-table" style="max-width: 500px; text-align: center;">
      <thead>
        <tr>
          <th>Actual \\ Predicted</th>
          ${labels.map((l) => `<th style="text-transform: capitalize;">${l}</th>`).join("")}
        </tr>
      </thead>
      <tbody>
  `;

  matrix.forEach((row, rIdx) => {
    html += `<tr><td style="font-weight: 700; text-transform: capitalize;">${labels[rIdx]}</td>`;
    row.forEach((val, cIdx) => {
      const isDiag = rIdx === cIdx;
      const bg = isDiag ? "var(--color-primary-soft)" : "transparent";
      html += `<td style="background: ${bg}; font-weight: ${isDiag ? "700" : "normal"}; font-size: 1rem;">${val}</td>`;
    });
    html += `</tr>`;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

function renderBaselineTable(baselines) {
  const container = document.getElementById("baseline-comparison-table");
  if (!container || !baselines) return;

  const rows = [
    { name: "Majority Class Baseline (Dummy)", data: baselines.majority_baseline },
    { name: "Multinomial Naive Bayes", data: baselines.multinomial_nb },
    { name: "Logistic Regression (Balanced Weights) [Primary]", data: baselines.logistic_regression },
  ];

  let html = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Candidate Model</th>
          <th>Accuracy</th>
          <th>Macro F1-Score</th>
          <th>Assessment</th>
        </tr>
      </thead>
      <tbody>
  `;

  rows.forEach((r, idx) => {
    const isPrimary = idx === 2;
    html += `
      <tr style="${isPrimary ? "font-weight: 700; background: var(--color-primary-soft);" : ""}">
        <td>${r.name}</td>
        <td>${(r.data.accuracy * 100).toFixed(1)}%</td>
        <td>${r.data.macro_f1.toFixed(4)}</td>
        <td>${isPrimary ? "Deployed Model" : "Baseline Benchmark"}</td>
      </tr>
    `;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

function renderScenarioTable(scenarios) {
  const container = document.getElementById("scenario-breakdown-table");
  if (!container || !scenarios) return;

  let html = `
    <table class="data-table">
      <thead>
        <tr>
          <th>Scenario ID</th>
          <th>Evaluation Query Focus</th>
          <th>Target Category</th>
          <th>Precision@5</th>
          <th>Recall@5</th>
          <th>NDCG@5</th>
        </tr>
      </thead>
      <tbody>
  `;

  scenarios.forEach((sc) => {
    html += `
      <tr>
        <td style="font-family: monospace; font-size: 0.8rem;">${sc.scenario_id}</td>
        <td>${sc.description}</td>
        <td><span class="badge-cat">${sc.category || "Any"}</span></td>
        <td>${sc.precision_at_k.toFixed(2)}</td>
        <td>${sc.recall_at_k.toFixed(2)}</td>
        <td>${sc.ndcg_at_k.toFixed(2)}</td>
      </tr>
    `;
  });

  html += `</tbody></table>`;
  container.innerHTML = html;
}

async function loadEDACharts() {
  const container = document.getElementById("eda-charts-gallery");
  if (!container) return;

  try {
    const res = await fetch("/api/eda/charts");
    if (!res.ok) throw new Error("Could not load charts.");
    const data = await res.json();

    container.innerHTML = data.charts
      .map(
        (c) => `
        <div class="chart-card">
          <h4 class="chart-title">${c.title}</h4>
          <p class="chart-desc">${c.description}</p>
          <img src="${c.url}" alt="${c.title}" loading="lazy" />
        </div>
      `
      )
      .join("");
  } catch (err) {
    container.innerHTML = `<p>Error loading charts: ${err.message}</p>`;
  }
}
