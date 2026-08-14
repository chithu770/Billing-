"""
POS Billing Frame: Category-wise product selection, cart management, customer details modal, calculations, and invoice creation.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from config import COLORS, FONTS
from database import (
    fetch_all_categories, fetch_products_by_category, 
    generate_bill_number, save_bill, fetch_all_products,
    fetch_store_settings
)
from utils.pdf_generator import generate_text_receipt, generate_pdf_invoice, get_active_store_settings

class PaymentModalDialog(tk.Toplevel):
    """Modal Dialog popup for entering/modifying customer details and payment cash change."""
    def __init__(self, parent, bill_no, net_total, initial_name="", initial_phone=""):
        super().__init__(parent)
        self.title(f"💳 Payment & Customer Details - Bill #{bill_no}")
        self.geometry("520x620")
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self.bill_no = bill_no
        self.net_total = net_total
        self.result = None

        st = get_active_store_settings()
        self.currency = st["currency_symbol"]

        self._create_widgets(initial_name, initial_phone)
        self.center_window(parent)

    def center_window(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

    def _create_widgets(self, initial_name, initial_phone):
        hdr = tk.Frame(self, bg=COLORS["header_bg"], padx=15, pady=12)
        hdr.pack(fill="x")

        tk.Label(hdr, text=f"Bill Invoice: {self.bill_no}", font=FONTS["subtitle"], bg=COLORS["header_bg"], fg="white").pack(side="left")
        tk.Label(hdr, text=f"Total: {self.currency}{self.net_total:.2f}", font=FONTS["title"], bg=COLORS["header_bg"], fg=COLORS["success"]).pack(side="right")

        body = tk.Frame(self, bg=COLORS["bg_card"], padx=18, pady=15)
        body.pack(fill="both", expand=True)

        # 1. Customer Details
        tk.Label(body, text="👤 Customer Information", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(body, text="Customer Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar(value=initial_name or "Walk-in Customer")
        ent_name = tk.Entry(body, textvariable=self.name_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        ent_name.grid(row=1, column=1, sticky="ew", pady=4, ipady=3)

        tk.Label(body, text="Phone Number:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=2, column=0, sticky="w", pady=4)
        self.phone_var = tk.StringVar(value=initial_phone)
        ent_phone = tk.Entry(body, textvariable=self.phone_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        ent_phone.grid(row=2, column=1, sticky="ew", pady=4, ipady=3)

        tk.Label(body, text="Email Address:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=3, column=0, sticky="w", pady=4)
        self.email_var = tk.StringVar()
        ent_email = tk.Entry(body, textvariable=self.email_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        ent_email.grid(row=3, column=1, sticky="ew", pady=4, ipady=3)

        tk.Label(body, text="Billing / Address:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=4, column=0, sticky="nw", pady=4)
        self.txt_address = tk.Text(body, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid", height=3)
        self.txt_address.grid(row=4, column=1, sticky="ew", pady=4)

        body.columnconfigure(1, weight=1)

        tk.Frame(body, height=1, bg=COLORS["border"]).grid(row=5, column=0, columnspan=2, sticky="ew", pady=10)

        # 2. Payment Details
        tk.Label(body, text="💰 Payment Mode & Cash Change Calculator", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(body, text="Payment Method:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=7, column=0, sticky="w", pady=4)
        self.pay_mode_var = tk.StringVar(value="Cash")
        combo_mode = ttk.Combobox(body, textvariable=self.pay_mode_var, values=["Cash", "UPI / QR", "Credit Card", "Debit Card", "Net Banking"], state="readonly")
        combo_mode.grid(row=7, column=1, sticky="ew", pady=4)
        combo_mode.bind("<<ComboboxSelected>>", self.on_pay_mode_change)

        tk.Label(body, text="Amount Tendered:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=8, column=0, sticky="w", pady=4)
        self.paid_var = tk.StringVar(value=f"{self.net_total:.2f}")
        self.ent_paid = tk.Entry(body, textvariable=self.paid_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        self.ent_paid.grid(row=8, column=1, sticky="ew", pady=4, ipady=3)
        self.paid_var.trace_add("write", lambda *args: self.calculate_change())

        tk.Label(body, text="Change Due to Customer:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=9, column=0, sticky="w", pady=4)
        self.lbl_change = tk.Label(body, text=f"{self.currency}0.00", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["success"])
        self.lbl_change.grid(row=9, column=1, sticky="w", pady=4)

        # Buttons
        btn_box = tk.Frame(body, bg=COLORS["bg_card"], pady=10)
        btn_box.grid(row=10, column=0, columnspan=2, sticky="ew")

        btn_confirm = tk.Button(
            btn_box, text="✅ Confirm Payment & Create Bill", font=FONTS["subtitle"],
            bg=COLORS["success"], fg="white", activebackground=COLORS["success_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=8,
            command=self.confirm_action
        )
        btn_confirm.pack(fill="x", pady=(0, 6))

        btn_cancel = tk.Button(
            btn_box, text="❌ Cancel", font=FONTS["body"],
            bg=COLORS["bg_card_alt"], fg=COLORS["text_light"], relief="flat", cursor="hand2", pady=4,
            command=self.destroy
        )
        btn_cancel.pack(fill="x")

        self.calculate_change()

    def on_pay_mode_change(self, event=None):
        mode = self.pay_mode_var.get()
        if mode != "Cash":
            self.paid_var.set(f"{self.net_total:.2f}")
            self.ent_paid.config(state="disabled")
        else:
            self.ent_paid.config(state="normal")
        self.calculate_change()

    def calculate_change(self):
        try:
            paid = float(self.paid_var.get())
            change = paid - self.net_total
            if change < 0:
                self.lbl_change.config(text=f"Short by {self.currency}{abs(change):.2f}", fg=COLORS["danger"])
            else:
                self.lbl_change.config(text=f"{self.currency}{change:.2f}", fg=COLORS["success"])
        except ValueError:
            self.lbl_change.config(text="Invalid Amount", fg=COLORS["danger"])

    def confirm_action(self):
        name = self.name_var.get().strip() or "Walk-in Customer"
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.txt_address.get("1.0", tk.END).strip()
        pay_mode = self.pay_mode_var.get()

        try:
            paid = float(self.paid_var.get())
            if pay_mode == "Cash" and paid < self.net_total:
                if not messagebox.askyesno("Underpaid Warning", f"Amount tendered ({self.currency}{paid:.2f}) is less than total amount ({self.currency}{self.net_total:.2f}). Proceed anyway?"):
                    return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid amount tendered.")
            return

        change = max(0.0, paid - self.net_total)
        self.result = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address,
            "payment_mode": pay_mode,
            "amount_paid": paid,
            "change_due": change
        }
        self.destroy()


class BillingFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller

        self.cart_items = []
        self.selected_category = "All"
        self.current_bill_no = generate_bill_number()
        
        self.currency = "$"
        self.tax_percentage = 5.0
        self.load_active_settings()

        self._create_widgets()
        self.load_categories()
        self.load_products()
        self.update_bill_summary()

    def load_active_settings(self):
        st = fetch_store_settings()
        self.currency = st.get("currency_symbol", "$")
        try:
            self.tax_percentage = float(st.get("tax_percentage", "5.0"))
        except ValueError:
            self.tax_percentage = 5.0

    def _create_widgets(self):
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=5)
        self.columnconfigure(2, weight=4)
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. LEFT PANEL: Category & Product Selection
        # ----------------------------------------------------
        left_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=10, pady=10, highlightbackground=COLORS["border"], highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.rowconfigure(3, weight=1)
        left_panel.columnconfigure(0, weight=1)

        cat_hdr = tk.Label(left_panel, text="1. Select Category & Product", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        cat_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.cat_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        self.cat_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        search_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        search_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        tk.Label(search_frame, text="🔍 Search:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_products())
        search_ent = tk.Entry(search_frame, textvariable=self.search_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", relief="solid", bd=1)
        search_ent.grid(row=0, column=1, sticky="ew", ipady=4)

        prod_table_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        prod_table_frame.grid(row=3, column=0, sticky="nsew")
        prod_table_frame.rowconfigure(0, weight=1)
        prod_table_frame.columnconfigure(0, weight=1)

        columns = ("code", "name", "price", "stock")
        self.prod_tree = ttk.Treeview(prod_table_frame, columns=columns, show="headings", selectmode="browse")
        self.prod_tree.heading("code", text="Code")
        self.prod_tree.heading("name", text="Product Name")
        self.prod_tree.heading("price", text="Price")
        self.prod_tree.heading("stock", text="Stock")

        self.prod_tree.column("code", width=70, anchor="center")
        self.prod_tree.column("name", width=150, anchor="w")
        self.prod_tree.column("price", width=80, anchor="e")
        self.prod_tree.column("stock", width=60, anchor="center")

        prod_vsb = ttk.Scrollbar(prod_table_frame, orient="vertical", command=self.prod_tree.yview)
        self.prod_tree.configure(yscrollcommand=prod_vsb.set)

        self.prod_tree.grid(row=0, column=0, sticky="nsew")
        prod_vsb.grid(row=0, column=1, sticky="ns")

        self.prod_tree.bind("<Double-1>", lambda e: self.add_to_cart())

        add_ctrl_frame = tk.Frame(left_panel, bg=COLORS["bg_card"], pady=8)
        add_ctrl_frame.grid(row=4, column=0, sticky="ew")
        
        tk.Label(add_ctrl_frame, text="Qty:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(side="left", padx=(0, 5))
        self.qty_spin = tk.Spinbox(add_ctrl_frame, from_=1, to=999, width=5, font=FONTS["body"], justify="center")
        self.qty_spin.pack(side="left", padx=(0, 10))

        btn_add = tk.Button(
            add_ctrl_frame, text="➕ Add to Cart", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", padx=12, pady=5,
            command=self.add_to_cart
        )
        btn_add.pack(side="left", fill="x", expand=True)

        # ----------------------------------------------------
        # 2. MIDDLE PANEL: Customer Details & Cart Items
        # ----------------------------------------------------
        mid_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=10, pady=10, highlightbackground=COLORS["border"], highlightthickness=1)
        mid_panel.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        mid_panel.rowconfigure(2, weight=1)
        mid_panel.columnconfigure(0, weight=1)

        cust_hdr = tk.Label(mid_panel, text="2. Customer Details & Cart", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        cust_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        cust_box = tk.LabelFrame(mid_panel, text="Customer Information", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], bd=1, relief="solid", padx=8, pady=8)
        cust_box.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        cust_box.columnconfigure(1, weight=1)
        cust_box.columnconfigure(3, weight=1)

        tk.Label(cust_box, text="Bill No:", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        self.lbl_bill_no = tk.Label(cust_box, text=self.current_bill_no, font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["secondary"])
        self.lbl_bill_no.grid(row=0, column=1, sticky="w", padx=(0, 10))

        tk.Label(cust_box, text="Payment Mode:", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=2, sticky="w")
        self.pay_mode_var = tk.StringVar(value="Cash")
        pay_combo = ttk.Combobox(cust_box, textvariable=self.pay_mode_var, values=["Cash", "UPI / QR", "Credit Card", "Debit Card", "Net Banking"], state="readonly", width=12)
        pay_combo.grid(row=0, column=3, sticky="ew")

        tk.Label(cust_box, text="Name:", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", pady=(5,0))
        self.cust_name_var = tk.StringVar(value="Walk-in Customer")
        cust_name_ent = tk.Entry(cust_box, textvariable=self.cust_name_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        cust_name_ent.grid(row=1, column=1, sticky="ew", pady=(5,0), padx=(0, 10))

        tk.Label(cust_box, text="Phone:", font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=1, column=2, sticky="w", pady=(5,0))
        self.cust_phone_var = tk.StringVar()
        cust_phone_ent = tk.Entry(cust_box, textvariable=self.cust_phone_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        cust_phone_ent.grid(row=1, column=3, sticky="ew", pady=(5,0))

        cart_table_frame = tk.Frame(mid_panel, bg=COLORS["bg_card"])
        cart_table_frame.grid(row=2, column=0, sticky="nsew")
        cart_table_frame.rowconfigure(0, weight=1)
        cart_table_frame.columnconfigure(0, weight=1)

        cart_cols = ("name", "category", "price", "qty", "total")
        self.cart_tree = ttk.Treeview(cart_table_frame, columns=cart_cols, show="headings", selectmode="browse")
        self.cart_tree.heading("name", text="Item Name")
        self.cart_tree.heading("category", text="Category")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("qty", text="Qty")
        self.cart_tree.heading("total", text="Total")

        self.cart_tree.column("name", width=140, anchor="w")
        self.cart_tree.column("category", width=90, anchor="w")
        self.cart_tree.column("price", width=70, anchor="e")
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("total", width=80, anchor="e")

        cart_vsb = ttk.Scrollbar(cart_table_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_vsb.set)

        self.cart_tree.grid(row=0, column=0, sticky="nsew")
        cart_vsb.grid(row=0, column=1, sticky="ns")

        cart_btn_frame = tk.Frame(mid_panel, bg=COLORS["bg_card"], pady=8)
        cart_btn_frame.grid(row=3, column=0, sticky="ew")

        btn_rem = tk.Button(
            cart_btn_frame, text="❌ Remove Item", font=FONTS["small"],
            bg=COLORS["danger"], fg="white", activebackground=COLORS["danger_hover"],
            activeforeground="white", relief="flat", cursor="hand2", command=self.remove_cart_item
        )
        btn_rem.pack(side="left", padx=(0, 5))

        btn_clear = tk.Button(
            cart_btn_frame, text="🗑️ Clear Cart", font=FONTS["small"],
            bg=COLORS["bg_card_alt"], fg=COLORS["text_light"], relief="flat", cursor="hand2",
            command=self.clear_cart
        )
        btn_clear.pack(side="left")

        # ----------------------------------------------------
        # 3. RIGHT PANEL: Bill Calculations & Receipt View
        # ----------------------------------------------------
        right_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=10, pady=10, highlightbackground=COLORS["border"], highlightthickness=1)
        right_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        rcpt_hdr = tk.Label(right_panel, text="3. Bill Preview & Payment", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        rcpt_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.txt_receipt = scrolledtext.ScrolledText(
            right_panel, font=FONTS["receipt"], bg="#111827", fg="#34d399",
            insertbackground="white", bd=1, relief="solid", state="normal", width=38
        )
        self.txt_receipt.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        summary_box = tk.Frame(right_panel, bg=COLORS["bg_card_alt"], padx=10, pady=10, bd=1, relief="solid")
        summary_box.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        summary_box.columnconfigure(1, weight=1)

        tk.Label(summary_box, text="Subtotal:", font=FONTS["body"], bg=COLORS["bg_card_alt"], fg=COLORS["text_muted"]).grid(row=0, column=0, sticky="w")
        self.lbl_subtotal = tk.Label(summary_box, text="0.00", font=FONTS["body_bold"], bg=COLORS["bg_card_alt"], fg=COLORS["text_light"])
        self.lbl_subtotal.grid(row=0, column=1, sticky="e")

        tk.Label(summary_box, text="Discount:", font=FONTS["body"], bg=COLORS["bg_card_alt"], fg=COLORS["text_muted"]).grid(row=1, column=0, sticky="w")
        self.disc_var = tk.StringVar(value="0.0")
        disc_ent = tk.Entry(summary_box, textvariable=self.disc_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], width=8, justify="right")
        disc_ent.grid(row=1, column=1, sticky="e")
        self.disc_var.trace_add("write", lambda *args: self.update_bill_summary())

        self.lbl_tax_title = tk.Label(summary_box, text=f"Tax (GST {self.tax_percentage}%):", font=FONTS["body"], bg=COLORS["bg_card_alt"], fg=COLORS["text_muted"])
        self.lbl_tax_title.grid(row=2, column=0, sticky="w")
        self.lbl_tax = tk.Label(summary_box, text="0.00", font=FONTS["body_bold"], bg=COLORS["bg_card_alt"], fg=COLORS["text_light"])
        self.lbl_tax.grid(row=2, column=1, sticky="e")

        tk.Frame(summary_box, height=1, bg=COLORS["border"]).grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        tk.Label(summary_box, text="NET TOTAL:", font=FONTS["header"], bg=COLORS["bg_card_alt"], fg=COLORS["text_light"]).grid(row=4, column=0, sticky="w")
        self.lbl_net_total = tk.Label(summary_box, text="0.00", font=FONTS["stat_value"], bg=COLORS["bg_card_alt"], fg=COLORS["success"])
        self.lbl_net_total.grid(row=4, column=1, sticky="e")

        btn_action_frame = tk.Frame(right_panel, bg=COLORS["bg_card"])
        btn_action_frame.grid(row=3, column=0, sticky="ew")

        btn_generate = tk.Button(
            btn_action_frame, text="💳 Payment & Generate Bill", font=FONTS["subtitle"],
            bg=COLORS["success"], fg="white", activebackground=COLORS["success_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=8,
            command=self.open_payment_modal
        )
        btn_generate.pack(fill="x", pady=(0, 5))

    def load_categories(self):
        self.load_active_settings()
        for widget in self.cat_frame.winfo_children():
            widget.destroy()

        categories = fetch_all_categories()
        cat_list = ["All"] + [c["name"] for c in categories]

        for cat in cat_list:
            is_active = (cat == self.selected_category)
            bg_col = COLORS["primary"] if is_active else COLORS["bg_card_alt"]
            fg_col = "white" if is_active else COLORS["text_light"]

            btn = tk.Button(
                self.cat_frame, text=cat, font=FONTS["small"],
                bg=bg_col, fg=fg_col, relief="flat", cursor="hand2", padx=8, pady=3,
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(side="left", padx=2, pady=2)

    def filter_by_category(self, category_name):
        self.selected_category = category_name
        self.load_categories()
        self.load_products()

    def load_products(self):
        self.load_active_settings()
        for item in self.prod_tree.get_children():
            self.prod_tree.delete(item)

        search_q = self.search_var.get()
        products = fetch_products_by_category(self.selected_category, search_q)

        self.prod_tree.heading("price", text=f"Price ({self.currency})")

        for p in products:
            stock_str = f"⚠️ {p['stock']}" if p['stock'] <= 5 else str(p['stock'])
            self.prod_tree.insert("", "end", iid=p["id"], values=(
                p["code"], p["name"], f"{self.currency}{p['price']:.2f}", stock_str
            ))

    def add_to_cart(self):
        selected = self.prod_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the list to add to cart.")
            return

        prod_id = int(selected[0])
        all_prods = fetch_all_products()
        prod = next((p for p in all_prods if p["id"] == prod_id), None)

        if not prod:
            return

        try:
            req_qty = int(self.qty_spin.get())
            if req_qty <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Please enter a valid positive integer quantity.")
            return

        existing_item = next((item for item in self.cart_items if item["product_id"] == prod_id), None)
        current_in_cart = existing_item["quantity"] if existing_item else 0
        total_requested = current_in_cart + req_qty

        if total_requested > prod["stock"]:
            messagebox.showerror("Insufficient Stock", f"Only {prod['stock']} units of '{prod['name']}' are available in stock.")
            return

        if existing_item:
            existing_item["quantity"] += req_qty
            existing_item["total_price"] = existing_item["quantity"] * existing_item["unit_price"]
        else:
            self.cart_items.append({
                "product_id": prod["id"],
                "product_name": prod["name"],
                "category_name": prod["category_name"],
                "unit_price": prod["price"],
                "quantity": req_qty,
                "total_price": prod["price"] * req_qty
            })

        self.refresh_cart_tree()
        self.update_bill_summary()

    def remove_cart_item(self):
        selected = self.cart_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select an item from the cart to remove.")
            return
        
        idx = int(selected[0])
        if 0 <= idx < len(self.cart_items):
            del self.cart_items[idx]
            self.refresh_cart_tree()
            self.update_bill_summary()

    def clear_cart(self):
        self.cart_items.clear()
        self.refresh_cart_tree()
        self.update_bill_summary()

    def refresh_cart_tree(self):
        self.load_active_settings()
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)

        self.cart_tree.heading("price", text=f"Price ({self.currency})")
        self.cart_tree.heading("total", text=f"Total ({self.currency})")

        for idx, item in enumerate(self.cart_items):
            self.cart_tree.insert("", "end", iid=str(idx), values=(
                item["product_name"],
                item["category_name"],
                f"{self.currency}{item['unit_price']:.2f}",
                item["quantity"],
                f"{self.currency}{item['total_price']:.2f}"
            ))

    def update_bill_summary(self):
        self.load_active_settings()
        subtotal = sum(item["total_price"] for item in self.cart_items)
        
        try:
            discount_val = float(self.disc_var.get()) if self.disc_var.get() else 0.0
        except ValueError:
            discount_val = 0.0

        taxable = max(0.0, subtotal - discount_val)
        tax_amount = taxable * (self.tax_percentage / 100.0)
        net_total = taxable + tax_amount

        self.lbl_tax_title.config(text=f"Tax (GST {self.tax_percentage}%):")
        self.lbl_subtotal.config(text=f"{self.currency}{subtotal:.2f}")
        self.lbl_tax.config(text=f"{self.currency}{tax_amount:.2f}")
        self.lbl_net_total.config(text=f"{self.currency}{net_total:.2f}")

        bill_obj = {
            "bill_no": self.current_bill_no,
            "customer_name": self.cust_name_var.get() or "Walk-in Customer",
            "customer_phone": self.cust_phone_var.get() or "N/A",
            "date_time": "Now (Draft)",
            "subtotal": subtotal,
            "discount_amount": discount_val,
            "tax_amount": tax_amount,
            "net_total": net_total,
            "payment_mode": self.pay_mode_var.get()
        }

        receipt_text = generate_text_receipt(bill_obj, self.cart_items)
        self.txt_receipt.config(state="normal")
        self.txt_receipt.delete("1.0", tk.END)
        self.txt_receipt.insert(tk.END, receipt_text)
        self.txt_receipt.config(state="disabled")

    def open_payment_modal(self):
        """Launches the Payment & Customer Details Modal popup."""
        if not self.cart_items:
            messagebox.showwarning("Cart Empty", "Cannot generate bill for an empty cart. Please add items first.")
            return

        subtotal = sum(item["total_price"] for item in self.cart_items)
        try:
            discount_val = float(self.disc_var.get())
        except ValueError:
            discount_val = 0.0

        taxable = max(0.0, subtotal - discount_val)
        tax_amount = taxable * (self.tax_percentage / 100.0)
        net_total = taxable + tax_amount

        modal = PaymentModalDialog(
            self,
            bill_no=self.current_bill_no,
            net_total=net_total,
            initial_name=self.cust_name_var.get(),
            initial_phone=self.cust_phone_var.get()
        )
        self.wait_window(modal)

        if modal.result:
            res = modal.result
            self.process_bill(res, subtotal, discount_val, tax_amount, net_total)

    def process_bill(self, res, subtotal, discount_val, tax_amount, net_total):
        cust_name = res["name"]
        cust_phone = res["phone"]
        cust_email = res["email"]
        cust_address = res["address"]
        pay_mode = res["payment_mode"]
        amount_paid = res["amount_paid"]
        change_due = res["change_due"]

        # 1. Save Bill in Database & update product stock
        date_time = save_bill(
            self.current_bill_no, cust_name, cust_phone,
            self.cart_items, subtotal, discount_val, tax_amount, net_total,
            payment_mode=pay_mode, customer_email=cust_email, customer_address=cust_address,
            amount_paid=amount_paid, change_due=change_due
        )

        bill_obj = {
            "bill_no": self.current_bill_no,
            "customer_name": cust_name,
            "customer_phone": cust_phone,
            "customer_email": cust_email,
            "customer_address": cust_address,
            "date_time": date_time,
            "subtotal": subtotal,
            "discount_amount": discount_val,
            "tax_amount": tax_amount,
            "net_total": net_total,
            "payment_mode": pay_mode,
            "amount_paid": amount_paid,
            "change_due": change_due
        }

        # 2. Generate PDF & TXT Invoice
        pdf_path = generate_pdf_invoice(bill_obj, self.cart_items)
        generate_text_receipt(bill_obj, self.cart_items)

        messagebox.showinfo("Bill Generated Successfully!", f"Bill #{self.current_bill_no} created!\nPDF saved at:\n{pdf_path}")

        # Auto open PDF on Windows
        try:
            os.startfile(pdf_path)
        except Exception:
            pass

        # 3. Reset Bill State for Next Customer
        self.current_bill_no = generate_bill_number()
        self.lbl_bill_no.config(text=self.current_bill_no)
        self.cart_items.clear()
        self.cust_name_var.set("Walk-in Customer")
        self.cust_phone_var.set("")
        self.disc_var.set("0.0")
        self.refresh_cart_tree()
        self.load_products()
        self.update_bill_summary()
        
        self.app_controller.refresh_all_views()
