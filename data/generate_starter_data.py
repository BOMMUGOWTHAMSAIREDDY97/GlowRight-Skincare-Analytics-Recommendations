"""Script to generate realistic, reproducible synthetic benchmark data for GlowRight.
All records are marked with is_demo=True and source='Synthetic Internship Benchmark Dataset'.
"""

import csv
import random
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent

PRODUCTS = [
    # Cleansers
    {
        "product_id": "GR-001",
        "product_name": "Gentle Hydrating Oat Cleanser",
        "brand": "Aura Botanica",
        "category": "Cleanser",
        "price": 16.50,
        "rating": 4.7,
        "review_count": 342,
        "ingredients": "Aqua, Oat Kernel Extract, Glycerin, Coco-Glucoside, Sodium Cocoyl Glycinate, Ceramide NP, Allantoin, Citric Acid, Phenoxyethanol",
        "description": "A soothing, non-foaming daily cream cleanser formulated with colloidal oat and ceramides to gently wash away impurities without stripping the natural barrier.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-002",
        "product_name": "Clarifying Salicylic Foam Wash",
        "brand": "DermClear Labs",
        "category": "Cleanser",
        "price": 22.00,
        "rating": 4.4,
        "review_count": 215,
        "ingredients": "Aqua, Sodium Laureth Sulfate, Cocamidopropyl Betaine, Salicylic Acid 2%, Zinc PCA, Tea Tree Leaf Oil, Niacinamide, Glycerin, Sodium Hydroxide",
        "description": "Purifying gel-to-foam wash targeting congested pores, blemish-prone skin, and excess sebum with 2% BHA and soothing zinc.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-003",
        "product_name": "Barrier Support Oil-to-Milk Cleanser",
        "brand": "Solis Skincare",
        "category": "Cleanser",
        "price": 28.00,
        "rating": 4.8,
        "review_count": 189,
        "ingredients": "Caprylic/Capric Triglyceride, Helianthus Annuus Seed Oil, Polyglyceryl-4 Oleate, Squalane, Tocopherol, Bisabolol, Chamomile Flower Extract",
        "description": "Luxurious oil cleanser that melts waterproof makeup and sunscreen, emulsifying into a gentle milk that leaves skin silky and nourished.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-004",
        "product_name": "Exfoliating Glycolic Jelly Cleanser",
        "brand": "Verdant Alchemy",
        "category": "Cleanser",
        "price": 24.50,
        "rating": 4.2,
        "review_count": 140,
        "ingredients": "Aqua, Glycolic Acid 3%, Coco-Betaine, Glycerin, Sodium Cocoyl Isethionate, Panthenol, Citrus Aurantium Dulcis Fruit Extract, Fragrance (Parfum)",
        "description": "Gentle daily AHA cleansing jelly designed to brighten dull skin and promote cell turnover while maintaining hydration.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-005",
        "product_name": "Centella Soothing Micellar Gel",
        "brand": "PureKare",
        "category": "Cleanser",
        "price": 14.00,
        "rating": 4.6,
        "review_count": 278,
        "ingredients": "Aqua, Centella Asiatica Extract, PEG-6 Caprylic/Capric Glycerides, Glycerin, Madecassoside, Betaine, Disodium EDTA, Ethylhexylglycerin",
        "description": "Rinse-optional micellar cleansing gel packed with soothing cica to instantly calm redness and remove everyday pollution.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Serums
    {
        "product_id": "GR-006",
        "product_name": "10% Niacinamide + Zinc Serum",
        "brand": "DermClear Labs",
        "category": "Serum",
        "price": 12.00,
        "rating": 4.5,
        "review_count": 620,
        "ingredients": "Aqua, Niacinamide 10%, Zinc PCA 1%, Dimethyl Isosorbide, Tamarindus Indica Seed Gum, Xanthan Gum, Phenoxyethanol, Chlorphenesin",
        "description": "High-strength blemish formula designed to refine enlarged pores, balance shine, and visibly even out skin tone.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-007",
        "product_name": "Triple Hyaluronic Acid Plumping Drops",
        "brand": "Aura Botanica",
        "category": "Serum",
        "price": 26.00,
        "rating": 4.8,
        "review_count": 480,
        "ingredients": "Aqua, Sodium Hyaluronate (Multi-Molecular), Glycerin, Panthenol (Vitamin B5), Polyglutamic Acid, Trehalose, Ethylhexylglycerin",
        "description": "Multi-depth moisture replenishment serum combining low, medium, and high molecular weight hyaluronic acids with smoothing polyglutamic acid.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-008",
        "product_name": "15% Pure Vitamin C + Ferulic Brightening Complex",
        "brand": "Solis Skincare",
        "category": "Serum",
        "price": 54.00,
        "rating": 4.6,
        "review_count": 310,
        "ingredients": "Aqua, L-Ascorbic Acid 15%, Ethoxydiglycol, Tocopherol (Vitamin E), Ferulic Acid 0.5%, Panthenol, Triethanolamine, Sodium Hyaluronate",
        "description": "Clinical-strength antioxidant serum that combats environmental free radicals, lightens dark hyperpigmentation, and stimulates radiance.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-009",
        "product_name": "0.3% Encapsulated Retinol Renewal Serum",
        "brand": "Solis Skincare",
        "category": "Serum",
        "price": 42.00,
        "rating": 4.4,
        "review_count": 290,
        "ingredients": "Aqua, Caprylic/Capric Triglyceride, Glycerin, Phospholipids, Retinol 0.3%, Bakuchiol, Ceramide EOP, Tocopherol, Dimethicone",
        "description": "Time-released microencapsulated retinol paired with plant bakuchiol to minimize fine lines, smooth rough texture, and reduce flaking.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-010",
        "product_name": "Multi-Peptide Youth Recovery Elixir",
        "brand": "Verdant Alchemy",
        "category": "Serum",
        "price": 68.00,
        "rating": 4.7,
        "review_count": 165,
        "ingredients": "Aqua, Glycerin, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Copper Tripeptide-1, Acetyl Hexapeptide-8, Sodium Hyaluronate, Hydroxyethylcellulose",
        "description": "Concentrated peptide matrix targeting skin elasticity, firmness, and natural collagen synthesis for revitalized resilience.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-011",
        "product_name": "Centella Calming Relief Ampoule",
        "brand": "PureKare",
        "category": "Serum",
        "price": 19.50,
        "rating": 4.9,
        "review_count": 520,
        "ingredients": "Centella Asiatica Extract 85%, Butylene Glycol, Glycerin, Madecassic Acid, Asiaticoside, Panthenol, Allantoin, Betaine",
        "description": "Intensive emergency relief ampoule that rapidly soothes acute irritation, strengthens sensitized moisture barriers, and calms heat sensations.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Moisturizers
    {
        "product_id": "GR-012",
        "product_name": "Ceramide Barrier Defense Cream",
        "brand": "Aura Botanica",
        "category": "Moisturizer",
        "price": 28.00,
        "rating": 4.8,
        "review_count": 590,
        "ingredients": "Aqua, Caprylic/Capric Triglyceride, Butyrospermum Parkii (Shea) Butter, Ceramide NP, Ceramide AP, Ceramide EOP, Phytosphingosine, Cholesterol, Glycerin, Carbomer",
        "description": "Rich nourishing lipid cream mimicking the natural 3:1:1 skin barrier composition to lock in moisture and protect dry, sensitive skin.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-013",
        "product_name": "Oil-Free Mattifying Water Gel",
        "brand": "DermClear Labs",
        "category": "Moisturizer",
        "price": 21.00,
        "rating": 4.3,
        "review_count": 340,
        "ingredients": "Aqua, Dimethicone, Glycerin, Silica, Niacinamide, Sodium Hyaluronate, Green Tea Leaf Extract, Ammonium Acryloyldimethyltaurate/VP Copolymer",
        "description": "Weightless, quick-absorbing water gel offering 24-hour hydration with a smooth matte finish, perfect for combination and oily complexions.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-014",
        "product_name": "Squalane Rich Peptide Cream",
        "brand": "Verdant Alchemy",
        "category": "Moisturizer",
        "price": 46.00,
        "rating": 4.7,
        "review_count": 210,
        "ingredients": "Aqua, Squalane (100% Plant-Derived), Cetearyl Olivate, Sorbitan Olivate, Palmitoyl Tripeptide-5, Shea Butter, Glycerin, Tocopherol",
        "description": "Deeply restorative moisturizer combining lightweight plant-derived squalane with collagen-boosting peptides for supple firmness.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-015",
        "product_name": "Cica Overnight Recovery Balm",
        "brand": "PureKare",
        "category": "Moisturizer",
        "price": 25.00,
        "rating": 4.6,
        "review_count": 180,
        "ingredients": "Aqua, Centella Asiatica Extract, Caprylic/Capric Triglyceride, Panthenol 5%, Madecassoside, Ceramide NP, Squalane, Beeswax",
        "description": "Velvety sleeping balm that cocoon sensitized skin overnight to repair barrier micro-damage and eliminate redness by morning.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-016",
        "product_name": "Ultra-Light Cloud Lotion with HA",
        "brand": "Aura Botanica",
        "category": "Moisturizer",
        "price": 18.00,
        "rating": 4.5,
        "review_count": 312,
        "ingredients": "Aqua, Glycerin, Propanediol, Sodium Hyaluronate, Betaine, Allantoin, Carbomer, Sodium Hydroxide, Ethylhexylglycerin",
        "description": "A breathable daily lotion that glides on like silk, providing lasting hydration without any greasy or suffocating residue.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Sunscreens
    {
        "product_id": "GR-017",
        "product_name": "Invisible Mineral Shield SPF 50",
        "brand": "Solis Skincare",
        "category": "Sunscreen",
        "price": 32.00,
        "rating": 4.6,
        "review_count": 425,
        "ingredients": "Zinc Oxide 18.5%, Titanium Dioxide 2.1%, Aqua, Isododecane, Butyloctyl Salicylate, Niacinamide, Bisabolol, Tocopherol",
        "description": "Sheer 100% mineral sunscreen providing broad-spectrum UVA/UVB protection with zero white cast and skin-soothing niacinamide.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-018",
        "product_name": "Hydra-Glow UV Fluid SPF 50+",
        "brand": "Aura Botanica",
        "category": "Sunscreen",
        "price": 27.50,
        "rating": 4.8,
        "review_count": 510,
        "ingredients": "Aqua, Ethylhexyl Triazone, Bis-Ethylhexyloxyphenol Methoxyphenyl Triazine, Glycerin, Hyaluronic Acid, Centella Asiatica, Silica, Tocopherol",
        "description": "Next-generation chemical UV filter fluid that feels like a lightweight essence, leaving skin dewy, radiant, and fully shielded.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-019",
        "product_name": "Matte Defense Oil-Control SPF 45",
        "brand": "DermClear Labs",
        "category": "Sunscreen",
        "price": 24.00,
        "rating": 4.2,
        "review_count": 280,
        "ingredients": "Aqua, Homosalate 10%, Octocrylene 6%, Zinc PCA, Silica, Niacinamide 2%, Tapioca Starch, Dimethicone, Phenoxyethanol",
        "description": "Non-comedogenic sunscreen lotion featuring sebum-absorbing silica beads for all-day shine reduction under heat and humidity.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-020",
        "product_name": "Gentle Mineral Sun Milk for Sensitive Skin SPF 30",
        "brand": "PureKare",
        "category": "Sunscreen",
        "price": 22.00,
        "rating": 4.5,
        "review_count": 195,
        "ingredients": "Zinc Oxide 16%, Aqua, Centella Asiatica Extract, Caprylic/Capric Triglyceride, Propanediol, Ceramide NP, Allantoin",
        "description": "Fragrance-free physical sunscreen formulated specifically for hypersensitive, reactive skin prone to flare-ups or rosacea.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Toners
    {
        "product_id": "GR-021",
        "product_name": "Milky Ceramide Hydrating Toner",
        "brand": "Aura Botanica",
        "category": "Toner",
        "price": 19.00,
        "rating": 4.9,
        "review_count": 650,
        "ingredients": "Aqua, Glycerin, Dipropylene Glycol, Ceramide NP, Sodium Hyaluronate, Panthenol, Betaine, Hydrogenated Lecithin, 1,2-Hexanediol",
        "description": "Rich comforting toner that infuses deep moisture layers into thirsty skin immediately after cleansing, priming for maximum absorption.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-022",
        "product_name": "BHA Clarifying Exfoliating Toner",
        "brand": "DermClear Labs",
        "category": "Toner",
        "price": 21.00,
        "rating": 4.3,
        "review_count": 410,
        "ingredients": "Aqua, Methylpropanediol, Butylene Glycol, Salicylic Acid 2%, Camellia Sinensis (Green Tea) Leaf Extract, Sodium Hydroxide, Tetrasodium EDTA",
        "description": "Pore-clearing liquid exfoliant formulated with 2% salicylic acid to dissolve sebum plugs and smooth uneven skin texture.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-023",
        "product_name": "Centella Herb Calming Toner",
        "brand": "PureKare",
        "category": "Toner",
        "price": 16.00,
        "rating": 4.7,
        "review_count": 320,
        "ingredients": "Centella Asiatica Extract 80%, Aqua, Butylene Glycol, Pentylene Glycol, Allantoin, Portulaca Oleracea Extract, Sodium Hyaluronate",
        "description": "Pure herb-infused toner that balances skin pH, reduces post-wash tightness, and dampens flush redness in seconds.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-024",
        "product_name": "Glow Tonic 5% Glycolic Exfoliator",
        "brand": "Verdant Alchemy",
        "category": "Toner",
        "price": 23.00,
        "rating": 4.4,
        "review_count": 390,
        "ingredients": "Aqua, Glycolic Acid 5%, Aloe Barbadensis Leaf Juice, Hamamelis Virginiana (Witch Hazel) Water, Glycerin, Fragrance (Parfum), Sodium Hydroxide",
        "description": "Cult-favorite radiance tonic gently sloughing off dead surface cells to unveil illuminated, glass-skin clarity.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Exfoliants
    {
        "product_id": "GR-025",
        "product_name": "AHA 30% + BHA 2% Peeling Solution",
        "brand": "DermClear Labs",
        "category": "Exfoliant",
        "price": 11.50,
        "rating": 4.2,
        "review_count": 820,
        "ingredients": "Glycolic Acid 30%, Aqua, Aloe Barbadensis Leaf Water, Sodium Hydroxide, Salicylic Acid 2%, Lactic Acid, Tartaric Acid, Daucus Carota Sativa Extract",
        "description": "Potent 10-minute exfoliating facial peeling mask that targets stubborn congestion, visible spots, and rough texture.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-026",
        "product_name": "Gentle Lactic Acid 5% + HA Surface Resurfacer",
        "brand": "Aura Botanica",
        "category": "Exfoliant",
        "price": 15.00,
        "rating": 4.7,
        "review_count": 275,
        "ingredients": "Aqua, Lactic Acid 5%, Glycerin, Sodium Hyaluronate Crosspolymer, Tasmannia Lanceolata Fruit/Leaf Extract, Pentylene Glycol, Propanediol",
        "description": "Mild, hydrating alpha hydroxy acid solution ideal for beginner exfoliators seeking a smoother complexion without stinging.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-027",
        "product_name": "Enzyme Powder Micro-Polish",
        "brand": "Verdant Alchemy",
        "category": "Exfoliant",
        "price": 34.00,
        "rating": 4.8,
        "review_count": 190,
        "ingredients": "Microcrystalline Cellulose, Oryza Sativa (Rice) Bran, Sodium Cocoyl Glycinate, Papain, Bromelain, Allantoin, Camellia Sinensis Leaf Powder",
        "description": "Water-activated rice bran powder infused with fruit enzymes that activates into a creamy lather to gently buff micro-roughness.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-028",
        "product_name": "PHA 8% Barrier-Safe Exfoliating Gel",
        "brand": "PureKare",
        "category": "Exfoliant",
        "price": 26.00,
        "rating": 4.6,
        "review_count": 160,
        "ingredients": "Aqua, Gluconolactone 8% (PHA), Lactobionic Acid, Centella Asiatica Extract, Glycerin, Panthenol, Sodium Hyaluronate",
        "description": "Non-irritating polyhydroxy acid resurfacing treatment engineered especially for sensitive skin with a compromised stratum corneum.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Eye Creams
    {
        "product_id": "GR-029",
        "product_name": "Caffeine + Peptide Eye Awakening Serum",
        "brand": "Solis Skincare",
        "category": "Eye Cream",
        "price": 29.00,
        "rating": 4.5,
        "review_count": 310,
        "ingredients": "Aqua, Caffeine 5%, Epigallocatechin Gallatyl Glucoside (EGCG), Palmitoyl Tripeptide-38, Glycerin, Sodium Hyaluronate, Hydroxyethylcellulose",
        "description": "Lightweight cooling fluid targeting morning puffy under-eyes, dark circles, and tired microcirculation.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-030",
        "product_name": "Ceramide & Avocado Rich Eye Balm",
        "brand": "Aura Botanica",
        "category": "Eye Cream",
        "price": 32.00,
        "rating": 4.7,
        "review_count": 240,
        "ingredients": "Aqua, Persea Gratissima (Avocado) Oil, Butyrospermum Parkii Butter, Ceramide NP, Squalane, Glycerin, Tocopherol, Bisabolol",
        "description": "Decadent, cushiony eye balm designed to quench dry crow's-feet, smooth crepey lids, and prevent moisture loss.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-031",
        "product_name": "Retinol Firming Eye Corrector",
        "brand": "Verdant Alchemy",
        "category": "Eye Cream",
        "price": 48.00,
        "rating": 4.3,
        "review_count": 185,
        "ingredients": "Aqua, Caprylic/Capric Triglyceride, Retinol 0.1%, Niacinamide, Caffeine, Ceramide AP, Squalane, Glyceryl Stearate",
        "description": "Low-dose buffered retinol emulsion clinically crafted for the delicate periorbital zone to diminish deep wrinkles over time.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Masks
    {
        "product_id": "GR-032",
        "product_name": "Kaolin Clay & Sulfur Detoxifying Mask",
        "brand": "DermClear Labs",
        "category": "Mask",
        "price": 20.00,
        "rating": 4.4,
        "review_count": 290,
        "ingredients": "Aqua, Kaolin, Bentonite, Sulfur 3%, Zinc Oxide, Glycerin, Tea Tree Leaf Oil, Phenoxyethanol, Iron Oxides",
        "description": "Mineral-rich pore clearing clay mask that draws out embedded impurities, absorbs oil, and reduces active blemishes.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-033",
        "product_name": "Deep Hydration Bio-Cellulose Sheet Mask (Pack of 5)",
        "brand": "Aura Botanica",
        "category": "Mask",
        "price": 25.00,
        "rating": 4.8,
        "review_count": 415,
        "ingredients": "Aqua, Butylene Glycol, Glycerin, Sodium Hyaluronate, Centella Asiatica Extract, Ceramide NP, Trehalose, Panthenol",
        "description": "Second-skin fermented coconut fiber sheets soaked in intensive barrier essence for an instant 20-minute hydration boost.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-034",
        "product_name": "Radiance Honey & Propolis Glow Mask",
        "brand": "Verdant Alchemy",
        "category": "Mask",
        "price": 38.00,
        "rating": 4.7,
        "review_count": 230,
        "ingredients": "Honey Extract 40%, Propolis Extract 15%, Aqua, Glycerin, Royal Jelly Extract, Niacinamide, Macadamia Seed Oil, Fragrance (Parfum)",
        "description": "Warm golden wash-off treatment packed with raw honey and propolis to deeply nourish, soothe, and ignite luminous glow.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-035",
        "product_name": "Cica Overnight Soothing Gel Mask",
        "brand": "PureKare",
        "category": "Mask",
        "price": 22.00,
        "rating": 4.6,
        "review_count": 195,
        "ingredients": "Aqua, Centella Asiatica Extract, Glycerin, Madecassoside, Allantoin, Aloe Barbadensis Leaf Juice, Carbomer, Arginine",
        "description": "Cooling sleep mask that calms flushed, irritated skin through the night with high-concentration cica and soothing aloe.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },

    # Additional diverse products for rich filtering & comparisons
    {
        "product_id": "GR-036",
        "product_name": "Barrier Recovery Squalane Facial Oil",
        "brand": "Aura Botanica",
        "category": "Moisturizer",
        "price": 32.00,
        "rating": 4.8,
        "review_count": 260,
        "ingredients": "Squalane (100% Sugarcane-Derived), Tocopherol (Vitamin E)",
        "description": "Pure plant squalane oil that locks in vital moisture, softens dry flakes, and enhances skin suppleness without clogging pores.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-037",
        "product_name": "Azelaic Acid 10% Clarifying Suspension",
        "brand": "DermClear Labs",
        "category": "Serum",
        "price": 14.50,
        "rating": 4.4,
        "review_count": 470,
        "ingredients": "Aqua, Azelaic Acid 10%, Isodecyl Neopentanoate, Dimethicone, Glycerin, Polysorbate 60, Polyacrylate Crosspolymer-6, Phenoxyethanol",
        "description": "Multi-action brightening cream-gel that visibly targets post-acne pigmentation marks, calms redness, and evens skin tone.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-038",
        "product_name": "Zinc & Tea Tree Clarifying Spot Gel",
        "brand": "DermClear Labs",
        "category": "Serum",
        "price": 9.50,
        "rating": 4.1,
        "review_count": 220,
        "ingredients": "Aqua, Alcohol Denat., Salicylic Acid, Melaleuca Alternifolia (Tea Tree) Leaf Oil, Zinc PCA, Hydroxyethylcellulose, Allantoin",
        "description": "Targeted fast-acting spot gel that visibly dries out emergency blemishes overnight while minimizing surrounding redness.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-039",
        "product_name": "Peptide & Ceramide Neck & Decollete Cream",
        "brand": "Verdant Alchemy",
        "category": "Moisturizer",
        "price": 58.00,
        "rating": 4.6,
        "review_count": 145,
        "ingredients": "Aqua, Caprylic/Capric Triglyceride, Shea Butter, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Ceramide NP, Squalane, Caffeine",
        "description": "Sculpting intensive neck cream focused on tightening sagging skin, horizontal neck lines, and delicate chest sun damage.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
    {
        "product_id": "GR-040",
        "product_name": "Soothing Mugwort Essence Toner",
        "brand": "PureKare",
        "category": "Toner",
        "price": 24.00,
        "rating": 4.7,
        "review_count": 310,
        "ingredients": "Artemisia Princeps (Mugwort) Extract 100%, Butylene Glycol, 1,2-Hexanediol",
        "description": "Single-ingredient botanical essence toner harnessing fermented Korean mugwort to soothe heated, reactive, and stressed skin.",
        "source": "Synthetic Internship Benchmark Dataset",
        "source_date": "2026-03-01",
        "is_demo": True,
    },
]

# Generate realistic reviews for each product with genuine sentiment nuances
REVIEW_TEMPLATES = {
    "positive": [
        "Absolutely love this {category}. The {ingredient} makes an immediate difference in hydration and my skin has never felt softer.",
        "This {category} from {brand} is a holy grail for my dry, sensitive skin. No irritation whatsoever and gives a gorgeous glow.",
        "Worth every penny. The texture is lightweight, absorbs quickly, and layers beautifully under makeup and sunscreen.",
        "I was skeptical at first, but after three weeks of consistent use, my redness has visibly calmed down. Highly recommend!",
        "Gentle yet effective. Finally found a {category} that does not break me out or cause allergic flare-ups.",
        "Incredible product! It delivers exactly what it promises without any greasy residue or strong artificial fragrance.",
        "My skin barrier was damaged from over-exfoliating and this restored it within days. Plump, calm, and hydrated skin.",
        "Super impressed with the ingredient list. High concentration of active ingredients at an honest, accessible price.",
    ],
    "neutral": [
        "It is an okay {category}. Decent hydration, but I did not notice any dramatic change in my skin texture after a month.",
        "The formula is fine and does not irritate, but the packaging pump occasionally gets stuck. Average for the price.",
        "Works moderately well, though it feels a bit heavier on my combination skin than I expected for daytime use.",
        "A pleasant basic {category}. It keeps my skin moisturized, but you can find comparable products for slightly less money.",
        "Does the job without fanfare. Mild scent that fades quickly, though I wish it had higher percentage of actives.",
        "Good everyday staple, but nothing revolutionary. Might repurchase if on sale, but still exploring alternatives.",
    ],
    "negative": [
        "Unfortunately this caused small bumps and clogged pores on my forehead within four days. Had to stop using it.",
        "Too drying for my sensitive skin. Left my face feeling tight, stinging, and uncomfortably red.",
        "Disappointed with the texture. It pilled terribly under my moisturizer and left a sticky, greasy film.",
        "The added fragrance was way too overwhelming for my reactive skin. Would not recommend if you are fragrance-sensitive.",
        "Did not see any difference at all. Overpriced for what essentially feels like basic glycerin water.",
        "Caused a noticeable breakout and burning sensation around my cheek area. Not suitable for my skin type.",
    ],
}

def generate_reviews():
    reviews = []
    rev_id = 1
    
    # Generate 3 to 6 reviews per product for healthy distribution (~160 reviews)
    for p in PRODUCTS:
        pid = p["product_id"]
        cat = p["category"].lower()
        brand = p["brand"]
        # Pick primary ingredient
        ing_parts = [i.strip() for i in p["ingredients"].split(",") if len(i.strip()) > 3]
        primary_ing = ing_parts[1] if len(ing_parts) > 1 else "key ingredient"

        # Distribution tailored to product rating
        # High rating -> mostly positive, some neutral, rare negative
        # Medium rating -> balanced
        if p["rating"] >= 4.7:
            weights = [0.70, 0.20, 0.10]
        elif p["rating"] >= 4.4:
            weights = [0.55, 0.30, 0.15]
        else:
            weights = [0.40, 0.35, 0.25]

        num_reviews = random.randint(3, 5)
        for _ in range(num_reviews):
            sentiment = random.choices(["positive", "neutral", "negative"], weights=weights)[0]
            template = random.choice(REVIEW_TEMPLATES[sentiment])
            text = template.format(category=cat, brand=brand, ingredient=primary_ing)
            
            # Rating corresponding to sentiment
            if sentiment == "positive":
                star = random.choice([4.0, 5.0, 5.0, 5.0])
            elif sentiment == "neutral":
                star = random.choice([3.0, 3.0, 4.0])
            else:
                star = random.choice([1.0, 1.0, 2.0])

            day = random.randint(1, 28)
            month = random.randint(1, 3)
            date_str = f"2026-0{month}-{day:02d}"

            reviews.append({
                "review_id": f"REV-{rev_id:04d}",
                "product_id": pid,
                "rating": star,
                "review_text": text,
                "date": date_str,
                "sentiment": sentiment,
                "is_demo": True,
            })
            rev_id += 1

    return reviews

def main():
    products_csv = DATA_DIR / "products_demo.csv"
    reviews_csv = DATA_DIR / "reviews_demo.csv"

    # Write products
    with open(products_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(PRODUCTS[0].keys()))
        writer.writeheader()
        writer.writerows(PRODUCTS)
    print(f"Wrote {len(PRODUCTS)} products to {products_csv}")

    # Write reviews
    reviews = generate_reviews()
    with open(reviews_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(reviews[0].keys()))
        writer.writeheader()
        writer.writerows(reviews)
    print(f"Wrote {len(reviews)} reviews to {reviews_csv}")

if __name__ == "__main__":
    main()
