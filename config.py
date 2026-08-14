"""
Application Configuration & Theme Settings for Category-Wise Billing Software
"""
import os

# Application Info
APP_TITLE = "SuperMart - Category-Wise Billing & Inventory System"
APP_VERSION = "2.0.0"

# Shop / Business Metadata
SHOP_NAME = "SUPERMART HYPERMARKET"
SHOP_ADDRESS = "123 Commercial Avenue, Suite 400, Tech City"
SHOP_PHONE = "+1 (800) 555-SUPER / +91 9876543210"
SHOP_EMAIL = "support@supermart.com"
SHOP_GSTIN = "33AAAAA0000A1Z5"

# Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(INVOICE_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "billing_database.db")

# Default Tax & Currency Settings
CURRENCY_SYMBOL = "$"
TAX_PERCENTAGE = 5.0  # 5% default tax / GST

# Modern Sleek Palette (Dark Slate / Indigo / Mint Accent)
COLORS = {
    "bg_dark": "#0f172a",        # Deep slate background
    "bg_card": "#1e293b",        # Card background
    "bg_card_alt": "#334155",    # Secondary card / hover
    "bg_input": "#0f172a",       # Entry box background
    "primary": "#6366f1",        # Indigo primary button/accent
    "primary_hover": "#4f46e5",  # Primary hover
    "secondary": "#3b82f6",      # Bright Blue
    "secondary_hover": "#2563eb",
    "success": "#10b981",        # Mint Green
    "success_hover": "#059669",
    "warning": "#f59e0b",        # Amber Warning
    "danger": "#ef4444",         # Rose Danger
    "danger_hover": "#dc2626",
    "text_light": "#f8fafc",     # Bright text
    "text_muted": "#94a3b8",     # Subtitle text
    "border": "#475569",         # Subtle border
    "header_bg": "#1e1b4b",      # Top app header banner
    "accent": "#ec4899",         # Pink accent badge
}

# Typography
FONT_FAMILY = "Segoe UI"
FONTS = {
    "title": (FONT_FAMILY, 16, "bold"),
    "subtitle": (FONT_FAMILY, 12, "bold"),
    "header": (FONT_FAMILY, 11, "bold"),
    "body": (FONT_FAMILY, 10, "normal"),
    "body_bold": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9, "normal"),
    "stat_value": (FONT_FAMILY, 20, "bold"),
    "receipt": ("Courier New", 10, "normal"),
}

# Default Pre-Populated Categories & Sample Products
DEFAULT_CATEGORIES = [
    ("Toys", "Interactive games, action figures, soft toys and educational kits"),
    ("Fruits", "Fresh organic fruits, seasonal berries, and imported produce"),
    ("Dresses", "Apparel, kids clothing, casual wear, and party outfits"),
    ("Ice Creams", "Gelato, popsicles, ice cream tubs, and dessert cones"),
    ("Groceries", "Daily essentials, grains, beverages, and household items"),
    ("Electronics", "Gadgets, accessories, headphones, and smart devices"),
]

DEFAULT_PRODUCTS = [
    # (code, name, category, price, stock, discount)
    # Toys
    ("TOY001", "Remote Control Car", "Toys", 29.99, 45, 5.0),
    ("TOY002", "Plush Teddy Bear", "Toys", 14.50, 60, 0.0),
    ("TOY003", "Lego Building Block Set", "Toys", 49.99, 30, 10.0),
    ("TOY004", "Wooden Puzzle Board", "Toys", 9.99, 25, 0.0),
    
    # Fruits
    ("FRU001", "Fresh Fuji Apples (1 kg)", "Fruits", 4.99, 100, 0.0),
    ("FRU002", "Organic Cavendish Bananas (1 Dozen)", "Fruits", 2.99, 120, 0.0),
    ("FRU003", "Alphonso Mangoes (1 Box)", "Fruits", 18.50, 40, 5.0),
    ("FRU004", "Seedless Black Grapes (500g)", "Fruits", 3.75, 50, 0.0),

    # Dresses
    ("DRS001", "Cotton Casual Summer Dress", "Dresses", 34.99, 35, 15.0),
    ("DRS002", "Men's Denim Jacket", "Dresses", 59.99, 20, 10.0),
    ("DRS003", "Kids Party Frock", "Dresses", 24.50, 40, 5.0),
    ("DRS004", "Graphic Cotton T-Shirt", "Dresses", 12.99, 85, 0.0),

    # Ice Creams
    ("ICE001", "Belgium Chocolate Ice Cream Tub (1L)", "Ice Creams", 8.99, 50, 5.0),
    ("ICE002", "Vanilla Bean Cone", "Ice Creams", 2.50, 150, 0.0),
    ("ICE003", "Strawberry Swirl Popsicle", "Ice Creams", 1.99, 110, 0.0),
    ("ICE004", "Butterscotch Sundae", "Ice Creams", 4.25, 45, 0.0),

    # Groceries
    ("GRO001", "Organic Basmati Rice (5 kg)", "Groceries", 15.99, 65, 0.0),
    ("GRO002", "Extra Virgin Olive Oil (1L)", "Groceries", 12.50, 40, 8.0),
    ("GRO003", "Whole Wheat Bread", "Groceries", 2.20, 90, 0.0),

    # Electronics
    ("ELE001", "Wireless Bluetooth Earbuds", "Electronics", 39.99, 25, 12.0),
    ("ELE002", "Fast Charging Power Bank 10000mAh", "Electronics", 22.50, 30, 5.0),
]
