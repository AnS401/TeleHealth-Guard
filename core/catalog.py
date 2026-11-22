"""MOCK DATA ONLY. Fictional brands; no real products, prices, or patients."""

BRANDS = [
    {"name": "Lumen Skin", "category": "Dermatology", "blurb": "Online skincare clinic.",
     "products": ["Acne care plan", "Anti-aging plan"], "from_price_usd": 39, "visit_required": True,
     "ships_to": "All 50 states"},
    {"name": "Northstar Weight", "category": "Weight Management", "blurb": "Medically supervised weight programs.",
     "products": ["Monthly coaching + clinician plan"], "from_price_usd": 79, "visit_required": True,
     "ships_to": "45 states"},
    {"name": "Calm Sleep Co", "category": "Sleep", "blurb": "Sleep programs and clinician follow-up.",
     "products": ["Sleep program"], "from_price_usd": 29, "visit_required": True, "ships_to": "All 50 states"},
    {"name": "Evergreen Men's Health", "category": "Men's Health", "blurb": "Men's wellness telehealth.",
     "products": ["Wellness plan"], "from_price_usd": 49, "visit_required": True, "ships_to": "48 states"},
    {"name": "Bloom Hair", "category": "Hair", "blurb": "Hair care plans from licensed clinicians.",
     "products": ["Hair care plan"], "from_price_usd": 25, "visit_required": True, "ships_to": "All 50 states"},
    {"name": "Harbor Allergy", "category": "Allergy", "blurb": "Seasonal allergy care online.",
     "products": ["Seasonal plan"], "from_price_usd": 35, "visit_required": True, "ships_to": "40 states"},
]

CATEGORY_KEYWORDS = {
    "skin": "Dermatology", "acne": "Dermatology", "derm": "Dermatology",
    "weight": "Weight Management", "sleep": "Sleep", "men's": "Men's Health", "mens": "Men's Health",
    "hair": "Hair", "allerg": "Allergy",
}

ORDERS = {
    "ORD-1001": {"brand": "Lumen Skin", "status": "Shipped", "carrier": "Mock Express", "eta": "2 business days"},
    "ORD-1002": {"brand": "Bloom Hair", "status": "Processing", "carrier": None, "eta": "Ships within 1 business day"},
    "ORD-1003": {"brand": "Calm Sleep Co", "status": "Delivered", "carrier": "Mock Express", "eta": "Delivered"},
}
