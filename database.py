"""
Database operations and connection manager for Category-Wise Billing Software
"""
import sqlite3
import datetime
from config import DB_PATH, DEFAULT_CATEGORIES, DEFAULT_PRODUCTS

def get_connection():
    """Returns SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables, updates schema, and seeds default dataset if empty."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Settings Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """)

        # 2. Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            );
        """)
        
        # 3. Products Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category_name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                discount REAL DEFAULT 0.0,
                FOREIGN KEY (category_name) REFERENCES categories (name) ON UPDATE CASCADE
            );
        """)
        
        # 4. Bills Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                bill_no TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                customer_email TEXT,
                customer_address TEXT,
                date_time TEXT NOT NULL,
                subtotal REAL NOT NULL,
                discount_amount REAL NOT NULL,
                tax_amount REAL NOT NULL,
                net_total REAL NOT NULL,
                payment_mode TEXT DEFAULT 'Cash',
                amount_paid REAL DEFAULT 0.0,
                change_due REAL DEFAULT 0.0
            );
        """)

        # Ensure schema migrations for existing bill tables
        for col_name, col_type in [("customer_email", "TEXT"), ("customer_address", "TEXT"), ("amount_paid", "REAL DEFAULT 0.0"), ("change_due", "REAL DEFAULT 0.0")]:
            try:
                cursor.execute(f"ALTER TABLE bills ADD COLUMN {col_name} {col_type};")
            except sqlite3.OperationalError:
                pass # Column already exists
        
        # 5. Bill Line Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_no TEXT NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                category_name TEXT NOT NULL,
                unit_price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (bill_no) REFERENCES bills (bill_no) ON DELETE CASCADE
            );
        """)
        
        conn.commit()

        # Seed settings if empty
        cursor.execute("SELECT COUNT(*) FROM settings")
        if cursor.fetchone()[0] == 0:
            default_settings = [
                ("shop_name", "SUPERMART HYPERMARKET"),
                ("shop_address", "123 Commercial Avenue, Suite 400, Tech City"),
                ("shop_phone", "+1 (800) 555-SUPER / +91 9876543210"),
                ("shop_email", "support@supermart.com"),
                ("shop_gstin", "33AAAAA0000A1Z5"),
                ("currency_symbol", "$"),
                ("tax_percentage", "5.0"),
                ("logo_path", "")
            ]
            cursor.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", default_settings)
            conn.commit()

        # Seed categories if empty
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            for name, desc in DEFAULT_CATEGORIES:
                cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, desc))
            conn.commit()

        # Seed products if empty
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            for code, name, category, price, stock, discount in DEFAULT_PRODUCTS:
                cursor.execute("""
                    INSERT INTO products (code, name, category_name, price, stock, discount)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, name, category, price, stock, discount))
            conn.commit()

# --- Settings Operations ---
def fetch_store_settings():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM settings")
        rows = cursor.fetchall()
        return {row["key"]: row["value"] for row in rows}

def update_store_settings(settings_dict):
    with get_connection() as conn:
        cursor = conn.cursor()
        for key, value in settings_dict.items():
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """, (key, str(value)))
        conn.commit()

# --- Category Operations ---
def fetch_all_categories():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]

def add_category(name, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name.strip(), description.strip()))
        conn.commit()
        return cursor.lastrowid

def update_category(cat_id, name, description, old_name=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE categories SET name = ?, description = ? WHERE id = ?", (name.strip(), description.strip(), cat_id))
        if old_name and old_name != name.strip():
            cursor.execute("UPDATE products SET category_name = ? WHERE category_name = ?", (name.strip(), old_name))
        conn.commit()

def delete_category(cat_id, cat_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products WHERE category_name = ?", (cat_name,))
        count = cursor.fetchone()[0]
        if count > 0:
            raise ValueError(f"Cannot delete category '{cat_name}'. It has {count} associated products.")
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()

# --- Product Operations ---
def fetch_all_products(search_term=""):
    with get_connection() as conn:
        cursor = conn.cursor()
        if search_term:
            query = "%" + search_term.strip() + "%"
            cursor.execute("""
                SELECT * FROM products 
                WHERE name LIKE ? OR code LIKE ? OR category_name LIKE ?
                ORDER BY name ASC
            """, (query, query, query))
        else:
            cursor.execute("SELECT * FROM products ORDER BY name ASC")
        return [dict(row) for row in cursor.fetchall()]

def fetch_products_by_category(category_name, search_term=""):
    with get_connection() as conn:
        cursor = conn.cursor()
        if category_name.lower() == "all":
            return fetch_all_products(search_term)
        
        if search_term:
            query = "%" + search_term.strip() + "%"
            cursor.execute("""
                SELECT * FROM products 
                WHERE category_name = ? AND (name LIKE ? OR code LIKE ?)
                ORDER BY name ASC
            """, (category_name, query, query))
        else:
            cursor.execute("SELECT * FROM products WHERE category_name = ? ORDER BY name ASC", (category_name,))
        return [dict(row) for row in cursor.fetchall()]

def add_product(code, name, category_name, price, stock, discount):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (code, name, category_name, price, stock, discount)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (code.strip().upper(), name.strip(), category_name, float(price), int(stock), float(discount)))
        conn.commit()
        return cursor.lastrowid

def update_product(prod_id, code, name, category_name, price, stock, discount):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET code = ?, name = ?, category_name = ?, price = ?, stock = ?, discount = ?
            WHERE id = ?
        """, (code.strip().upper(), name.strip(), category_name, float(price), int(stock), float(discount), prod_id))
        conn.commit()

def delete_product(prod_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (prod_id,))
        conn.commit()

# --- Billing Operations ---
def generate_bill_number():
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bills WHERE bill_no LIKE ?", (f"BILL-{date_str}-%",))
        seq = cursor.fetchone()[0] + 1
        return f"BILL-{date_str}-{seq:04d}"

def save_bill(bill_no, customer_name, customer_phone, items, subtotal, discount_amount, tax_amount, net_total, payment_mode="Cash", customer_email="", customer_address="", amount_paid=0.0, change_due=0.0):
    date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bills (bill_no, customer_name, customer_phone, customer_email, customer_address, date_time, subtotal, discount_amount, tax_amount, net_total, payment_mode, amount_paid, change_due)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (bill_no, customer_name.strip(), customer_phone.strip(), customer_email.strip(), customer_address.strip(), date_time, subtotal, discount_amount, tax_amount, net_total, payment_mode, float(amount_paid), float(change_due)))

        for item in items:
            cursor.execute("""
                INSERT INTO bill_items (bill_no, product_id, product_name, category_name, unit_price, quantity, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                bill_no,
                item.get('product_id'),
                item['product_name'],
                item['category_name'],
                float(item['unit_price']),
                int(item['quantity']),
                float(item['total_price'])
            ))

            # Deduct sold quantity from stock
            if item.get('product_id'):
                cursor.execute("""
                    UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
                """, (int(item['quantity']), item['product_id']))

        conn.commit()
        return date_time

def fetch_all_bills(search_query=""):
    with get_connection() as conn:
        cursor = conn.cursor()
        if search_query:
            q = "%" + search_query.strip() + "%"
            cursor.execute("""
                SELECT * FROM bills 
                WHERE bill_no LIKE ? OR customer_name LIKE ? OR customer_phone LIKE ?
                ORDER BY date_time DESC
            """, (q, q, q))
        else:
            cursor.execute("SELECT * FROM bills ORDER BY date_time DESC")
        return [dict(row) for row in cursor.fetchall()]

def fetch_bill_details(bill_no):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bills WHERE bill_no = ?", (bill_no,))
        bill_row = cursor.fetchone()
        if not bill_row:
            return None, []
        
        cursor.execute("SELECT * FROM bill_items WHERE bill_no = ?", (bill_no,))
        item_rows = cursor.fetchall()
        return dict(bill_row), [dict(item) for item in item_rows]

# --- Dashboard & Analytics Operations ---
def fetch_dashboard_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COALESCE(SUM(net_total), 0) FROM bills")
        total_revenue = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bills")
        total_bills = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products WHERE stock <= 5")
        low_stock_count = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category_name, SUM(total_price) as category_revenue, SUM(quantity) as items_sold
            FROM bill_items
            GROUP BY category_name
            ORDER BY category_revenue DESC
        """)
        category_stats = [dict(row) for row in cursor.fetchall()]

        return {
            "total_revenue": total_revenue,
            "total_bills": total_bills,
            "total_products": total_products,
            "low_stock_count": low_stock_count,
            "category_stats": category_stats
        }
