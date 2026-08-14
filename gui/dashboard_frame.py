"""
Sales Analytics & Dashboard Frame.
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, CURRENCY_SYMBOL
from database import fetch_dashboard_stats, fetch_all_products

class DashboardFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller

        self._create_widgets()
        self.load_dashboard_data()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # 1. Header Banner
        hdr_frame = tk.Frame(self, bg=COLORS["bg_card"], padx=15, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        hdr_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        tk.Label(hdr_frame, text="📊 Store Overview & Analytics Dashboard", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(side="left")
        
        btn_refresh = tk.Button(
            hdr_frame, text="🔄 Refresh Data", font=FONTS["small"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", padx=10, pady=4,
            command=self.load_dashboard_data
        )
        btn_refresh.pack(side="right")

        # 2. KPI Metric Stat Cards (4 Columns Grid)
        kpi_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        kpi_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        for i in range(4):
            kpi_frame.columnconfigure(i, weight=1)

        self.kpi_cards = {}
        card_configs = [
            ("total_revenue", "💵 Total Revenue", COLORS["success"]),
            ("total_bills", "🧾 Bills Generated", COLORS["secondary"]),
            ("total_products", "📦 Active Products", COLORS["primary"]),
            ("low_stock_count", "⚠️ Low Stock Items", COLORS["danger"]),
        ]

        for idx, (key, label_text, accent_color) in enumerate(card_configs):
            card = tk.Frame(kpi_frame, bg=COLORS["bg_card"], padx=15, pady=12, highlightbackground=accent_color, highlightthickness=2)
            card.grid(row=0, column=idx, sticky="ew", padx=5)

            tk.Label(card, text=label_text, font=FONTS["header"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).pack(anchor="w")
            
            val_lbl = tk.Label(card, text="0", font=FONTS["stat_value"], bg=COLORS["bg_card"], fg=accent_color)
            val_lbl.pack(anchor="w", pady=(5, 0))
            
            self.kpi_cards[key] = val_lbl

        # 3. Analytics Tables (2 Columns: Category Sales Breakdown & Low Stock Alert List)
        tables_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        tables_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        tables_frame.columnconfigure(0, weight=1)
        tables_frame.columnconfigure(1, weight=1)
        tables_frame.rowconfigure(0, weight=1)

        # 3A. Category Sales Table
        cat_box = tk.Frame(tables_frame, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        cat_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        cat_box.rowconfigure(1, weight=1)
        cat_box.columnconfigure(0, weight=1)

        tk.Label(cat_box, text="📈 Sales Revenue by Product Category", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).grid(row=0, column=0, sticky="w", pady=(0, 8))

        cat_table_frame = tk.Frame(cat_box, bg=COLORS["bg_card"])
        cat_table_frame.grid(row=1, column=0, sticky="nsew")
        cat_table_frame.rowconfigure(0, weight=1)
        cat_table_frame.columnconfigure(0, weight=1)

        cat_cols = ("category", "items_sold", "revenue")
        self.cat_tree = ttk.Treeview(cat_table_frame, columns=cat_cols, show="headings")
        self.cat_tree.heading("category", text="Category")
        self.cat_tree.heading("items_sold", text="Items Sold")
        self.cat_tree.heading("revenue", text=f"Revenue ({CURRENCY_SYMBOL})")

        self.cat_tree.column("category", width=140, anchor="w")
        self.cat_tree.column("items_sold", width=90, anchor="center")
        self.cat_tree.column("revenue", width=110, anchor="e")

        cat_vsb = ttk.Scrollbar(cat_table_frame, orient="vertical", command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=cat_vsb.set)
        self.cat_tree.grid(row=0, column=0, sticky="nsew")
        cat_vsb.grid(row=0, column=1, sticky="ns")

        # 3B. Low Stock Items Table
        stock_box = tk.Frame(tables_frame, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        stock_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        stock_box.rowconfigure(1, weight=1)
        stock_box.columnconfigure(0, weight=1)

        tk.Label(stock_box, text="🚨 Inventory Alert: Low Stock Products", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["danger"]).grid(row=0, column=0, sticky="w", pady=(0, 8))

        stock_table_frame = tk.Frame(stock_box, bg=COLORS["bg_card"])
        stock_table_frame.grid(row=1, column=0, sticky="nsew")
        stock_table_frame.rowconfigure(0, weight=1)
        stock_table_frame.columnconfigure(0, weight=1)

        stock_cols = ("name", "category", "price", "stock")
        self.stock_tree = ttk.Treeview(stock_table_frame, columns=stock_cols, show="headings")
        self.stock_tree.heading("name", text="Product Name")
        self.stock_tree.heading("category", text="Category")
        self.stock_tree.heading("price", text=f"Price ({CURRENCY_SYMBOL})")
        self.stock_tree.heading("stock", text="Remaining")

        self.stock_tree.column("name", width=150, anchor="w")
        self.stock_tree.column("category", width=100, anchor="w")
        self.stock_tree.column("price", width=70, anchor="e")
        self.stock_tree.column("stock", width=70, anchor="center")

        stock_vsb = ttk.Scrollbar(stock_table_frame, orient="vertical", command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=stock_vsb.set)
        self.stock_tree.grid(row=0, column=0, sticky="nsew")
        stock_vsb.grid(row=0, column=1, sticky="ns")

    def load_dashboard_data(self):
        stats = fetch_dashboard_stats()

        self.kpi_cards["total_revenue"].config(text=f"{CURRENCY_SYMBOL}{stats['total_revenue']:.2f}")
        self.kpi_cards["total_bills"].config(text=str(stats['total_bills']))
        self.kpi_cards["total_products"].config(text=str(stats['total_products']))
        self.kpi_cards["low_stock_count"].config(text=str(stats['low_stock_count']))

        # Load Category breakdown
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        for cat_stat in stats["category_stats"]:
            self.cat_tree.insert("", "end", values=(
                cat_stat["category_name"],
                cat_stat["items_sold"],
                f"{cat_stat['category_revenue']:.2f}"
            ))

        # Load Low Stock Products
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)

        all_products = fetch_all_products()
        low_stock_prods = [p for p in all_products if p["stock"] <= 10]
        low_stock_prods.sort(key=lambda p: p["stock"])

        for p in low_stock_prods:
            self.stock_tree.insert("", "end", values=(
                p["name"], p["category_name"], f"{p['price']:.2f}", f"⚠️ {p['stock']}"
            ))
