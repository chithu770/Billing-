"""
Product Inventory & Stock Management Frame (CRUD).
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS, CURRENCY_SYMBOL
from database import (
    fetch_all_products, fetch_all_categories, 
    add_product, update_product, delete_product
)

class ProductsFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller
        self.selected_product_id = None

        self._create_widgets()
        self.load_categories_combo()
        self.load_products()

    def _create_widgets(self):
        self.columnconfigure(0, weight=3) # Left: Product Table
        self.columnconfigure(1, weight=2) # Right: Add/Edit Product Form
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. LEFT PANEL: Product Table & Filters
        # ----------------------------------------------------
        left_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.rowconfigure(2, weight=1)
        left_panel.columnconfigure(0, weight=1)

        # Header
        hdr = tk.Label(left_panel, text="📦 Product Inventory & Stock Manager", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Filter Bar
        filter_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)

        tk.Label(filter_frame, text="🔍 Search:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_products())
        search_ent = tk.Entry(filter_frame, textvariable=self.search_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", relief="solid", bd=1)
        search_ent.grid(row=0, column=1, sticky="ew", padx=(0, 15), ipady=3)

        tk.Label(filter_frame, text="Category:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=2, padx=(0, 5))
        self.cat_filter_var = tk.StringVar(value="All")
        self.cat_filter_combo = ttk.Combobox(filter_frame, textvariable=self.cat_filter_var, state="readonly", width=15)
        self.cat_filter_combo.grid(row=0, column=3, sticky="e")
        self.cat_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_products())

        # Product Table (Treeview)
        table_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("id", "code", "name", "category", "price", "stock", "discount")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("code", text="Code")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("price", text=f"Price ({CURRENCY_SYMBOL})")
        self.tree.heading("stock", text="Stock Qty")
        self.tree.heading("discount", text="Discount %")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("code", width=75, anchor="center")
        self.tree.column("name", width=160, anchor="w")
        self.tree.column("category", width=100, anchor="w")
        self.tree.column("price", width=80, anchor="e")
        self.tree.column("stock", width=70, anchor="center")
        self.tree.column("discount", width=75, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)

        # Legend / Info Bar
        info_lbl = tk.Label(left_panel, text="* Products with stock ≤ 5 are marked with low-stock warning alerts.", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["warning"], anchor="w")
        info_lbl.grid(row=3, column=0, sticky="ew", pady=(8, 0))

        # ----------------------------------------------------
        # 2. RIGHT PANEL: Product Details Form (Add / Edit)
        # ----------------------------------------------------
        right_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.columnconfigure(1, weight=1)

        form_hdr = tk.Label(right_panel, text="✏️ Product Details Form", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        form_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Form Fields
        fields = [
            ("Product Code / SKU:", "code"),
            ("Product Name:", "name"),
            ("Category:", "category"),
            (f"Unit Price ({CURRENCY_SYMBOL}):", "price"),
            ("Stock Quantity:", "stock"),
            ("Discount Rate (%):", "discount"),
        ]

        self.form_vars = {}
        for idx, (label_text, key) in enumerate(fields, start=1):
            tk.Label(right_panel, text=label_text, font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=idx, column=0, sticky="w", pady=6)
            
            if key == "category":
                var = tk.StringVar()
                widget = ttk.Combobox(right_panel, textvariable=var, state="readonly", font=FONTS["body"])
                self.form_cat_combo = widget
            else:
                var = tk.StringVar()
                widget = tk.Entry(right_panel, textvariable=var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
            
            widget.grid(row=idx, column=1, sticky="ew", pady=6, ipady=3)
            self.form_vars[key] = var

        # Action Buttons
        btn_box = tk.Frame(right_panel, bg=COLORS["bg_card"], pady=15)
        btn_box.grid(row=7, column=0, columnspan=2, sticky="ew")

        self.btn_save = tk.Button(
            btn_box, text="➕ Add Product", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            command=self.save_product
        )
        self.btn_save.pack(fill="x", pady=(0, 6))

        self.btn_update = tk.Button(
            btn_box, text="💾 Update Product", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg="white", activebackground=COLORS["secondary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.update_product_action
        )
        self.btn_update.pack(fill="x", pady=(0, 6))

        self.btn_delete = tk.Button(
            btn_box, text="🗑️ Delete Product", font=FONTS["body_bold"],
            bg=COLORS["danger"], fg="white", activebackground=COLORS["danger_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.delete_product_action
        )
        self.btn_delete.pack(fill="x", pady=(0, 6))

        btn_clear = tk.Button(
            btn_box, text="🔄 Clear Form", font=FONTS["body"],
            bg=COLORS["bg_card_alt"], fg=COLORS["text_light"], relief="flat", cursor="hand2", pady=4,
            command=self.clear_form
        )
        btn_clear.pack(fill="x")

    def load_categories_combo(self):
        categories = fetch_all_categories()
        cat_names = [c["name"] for c in categories]
        self.cat_filter_combo["values"] = ["All"] + cat_names
        self.form_cat_combo["values"] = cat_names
        if cat_names and not self.form_vars["category"].get():
            self.form_vars["category"].set(cat_names[0])

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_q = self.search_var.get()
        cat_q = self.cat_filter_var.get()

        all_prods = fetch_all_products(search_q)
        if cat_q != "All":
            all_prods = [p for p in all_prods if p["category_name"] == cat_q]

        for p in all_prods:
            stock_disp = f"⚠️ {p['stock']}" if p['stock'] <= 5 else str(p['stock'])
            self.tree.insert("", "end", iid=str(p["id"]), values=(
                p["id"], p["code"], p["name"], p["category_name"],
                f"{p['price']:.2f}", stock_disp, f"{p['discount']:.1f}%"
            ))

    def on_product_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        prod_id = int(selected[0])
        all_prods = fetch_all_products()
        prod = next((p for p in all_prods if p["id"] == prod_id), None)
        if not prod:
            return

        self.selected_product_id = prod_id
        self.form_vars["code"].set(prod["code"])
        self.form_vars["name"].set(prod["name"])
        self.form_vars["category"].set(prod["category_name"])
        self.form_vars["price"].set(str(prod["price"]))
        self.form_vars["stock"].set(str(prod["stock"]))
        self.form_vars["discount"].set(str(prod["discount"]))

        self.btn_save.config(state="disabled")
        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")

    def clear_form(self):
        self.selected_product_id = None
        for key, var in self.form_vars.items():
            if key == "category":
                cat_names = self.form_cat_combo["values"]
                var.set(cat_names[0] if cat_names else "")
            else:
                var.set("")

        self.tree.selection_remove(self.tree.selection())
        self.btn_save.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")

    def save_product(self):
        code = self.form_vars["code"].get().strip()
        name = self.form_vars["name"].get().strip()
        category = self.form_vars["category"].get().strip()
        price_str = self.form_vars["price"].get().strip()
        stock_str = self.form_vars["stock"].get().strip()
        disc_str = self.form_vars["discount"].get().strip() or "0.0"

        if not code or not name or not category or not price_str or not stock_str:
            messagebox.showwarning("Incomplete Form", "Please fill in all mandatory product fields.")
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            discount = float(disc_str)
            if price < 0 or stock < 0 or discount < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Input", "Price, Stock, and Discount must be valid non-negative numbers.")
            return

        try:
            add_product(code, name, category, price, stock, discount)
            messagebox.showinfo("Success", f"Product '{name}' added successfully!")
            self.clear_form()
            self.load_products()
            self.app_controller.refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Database Error", f"Could not add product:\n{ex}")

    def update_product_action(self):
        if not self.selected_product_id:
            return

        code = self.form_vars["code"].get().strip()
        name = self.form_vars["name"].get().strip()
        category = self.form_vars["category"].get().strip()
        price_str = self.form_vars["price"].get().strip()
        stock_str = self.form_vars["stock"].get().strip()
        disc_str = self.form_vars["discount"].get().strip() or "0.0"

        if not code or not name or not category or not price_str or not stock_str:
            messagebox.showwarning("Incomplete Form", "Please fill in all mandatory product fields.")
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
            discount = float(disc_str)
        except ValueError:
            messagebox.showerror("Invalid Input", "Price, Stock, and Discount must be valid non-negative numbers.")
            return

        try:
            update_product(self.selected_product_id, code, name, category, price, stock, discount)
            messagebox.showinfo("Success", f"Product '{name}' updated successfully!")
            self.clear_form()
            self.load_products()
            self.app_controller.refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Database Error", f"Could not update product:\n{ex}")

    def delete_product_action(self):
        if not self.selected_product_id:
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product? This action cannot be undone."):
            try:
                delete_product(self.selected_product_id)
                messagebox.showinfo("Deleted", "Product removed successfully.")
                self.clear_form()
                self.load_products()
                self.app_controller.refresh_all_views()
            except Exception as ex:
                messagebox.showerror("Database Error", f"Could not delete product:\n{ex}")
