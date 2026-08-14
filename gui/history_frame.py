"""
Invoice History & Past Bills Viewer Frame.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from config import COLORS, FONTS, CURRENCY_SYMBOL, INVOICE_DIR
from database import fetch_all_bills, fetch_bill_details
from utils.pdf_generator import generate_text_receipt, generate_pdf_invoice

class HistoryFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller
        self.selected_bill_no = None

        self._create_widgets()
        self.load_bills()

    def _create_widgets(self):
        self.columnconfigure(0, weight=3) # Left: Bills Table
        self.columnconfigure(1, weight=3) # Right: Bill Details & Receipt preview
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. LEFT PANEL: Saved Bills Table & Search
        # ----------------------------------------------------
        left_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.rowconfigure(2, weight=1)
        left_panel.columnconfigure(0, weight=1)

        hdr = tk.Label(left_panel, text="📜 Sales & Invoice History", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Search Bar
        search_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        tk.Label(search_frame, text="🔍 Search Bill:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.load_bills())
        search_ent = tk.Entry(search_frame, textvariable=self.search_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", relief="solid", bd=1)
        search_ent.grid(row=0, column=1, sticky="ew", ipady=3)

        # Bills Treeview
        table_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        table_frame.grid(row=2, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("bill_no", "date", "customer", "phone", "total", "pay_mode")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("bill_no", text="Bill No")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("customer", text="Customer")
        self.tree.heading("phone", text="Phone")
        self.tree.heading("total", text=f"Total ({CURRENCY_SYMBOL})")
        self.tree.heading("pay_mode", text="Payment")

        self.tree.column("bill_no", width=110, anchor="center")
        self.tree.column("date", width=125, anchor="center")
        self.tree.column("customer", width=120, anchor="w")
        self.tree.column("phone", width=90, anchor="center")
        self.tree.column("total", width=80, anchor="e")
        self.tree.column("pay_mode", width=80, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_bill_select)

        # ----------------------------------------------------
        # 2. RIGHT PANEL: Selected Bill Receipt Inspector
        # ----------------------------------------------------
        right_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.rowconfigure(1, weight=1)
        right_panel.columnconfigure(0, weight=1)

        detail_hdr = tk.Label(right_panel, text="📄 Receipt Details & Inspector", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        detail_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Receipt Text Viewer Widget
        self.txt_receipt = scrolledtext.ScrolledText(
            right_panel, font=FONTS["receipt"], bg="#111827", fg="#34d399",
            insertbackground="white", bd=1, relief="solid", state="normal"
        )
        self.txt_receipt.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # Action Buttons
        btn_box = tk.Frame(right_panel, bg=COLORS["bg_card"])
        btn_box.grid(row=2, column=0, sticky="ew")

        self.btn_pdf = tk.Button(
            btn_box, text="📥 Open PDF Invoice", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.open_pdf
        )
        self.btn_pdf.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_reprint = tk.Button(
            btn_box, text="🖨️ Regenerate PDF/TXT", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg="white", activebackground=COLORS["secondary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.regenerate_files
        )
        self.btn_reprint.pack(side="left", fill="x", expand=True)

    def load_bills(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_q = self.search_var.get()
        bills = fetch_all_bills(search_q)

        for b in bills:
            self.tree.insert("", "end", iid=b["bill_no"], values=(
                b["bill_no"], b["date_time"], b["customer_name"],
                b["customer_phone"] or "N/A", f"{b['net_total']:.2f}", b["payment_mode"]
            ))

    def on_bill_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        bill_no = selected[0]
        self.selected_bill_no = bill_no

        bill_row, item_rows = fetch_bill_details(bill_no)
        if bill_row:
            receipt_text = generate_text_receipt(bill_row, item_rows)
            self.txt_receipt.config(state="normal")
            self.txt_receipt.delete("1.0", tk.END)
            self.txt_receipt.insert(tk.END, receipt_text)
            self.txt_receipt.config(state="disabled")

            self.btn_pdf.config(state="normal")
            self.btn_reprint.config(state="normal")

    def open_pdf(self):
        if not self.selected_bill_no:
            return
        
        pdf_path = os.path.join(INVOICE_DIR, f"{self.selected_bill_no}.pdf")
        if not os.path.exists(pdf_path):
            # Regenerate if missing
            self.regenerate_files()

        try:
            os.startfile(pdf_path)
        except Exception as ex:
            messagebox.showerror("Error Opening PDF", f"Could not launch PDF viewer:\n{ex}")

    def regenerate_files(self):
        if not self.selected_bill_no:
            return

        bill_row, item_rows = fetch_bill_details(self.selected_bill_no)
        if bill_row:
            pdf_path = generate_pdf_invoice(bill_row, item_rows)
            generate_text_receipt(bill_row, item_rows)
            messagebox.showinfo("Invoice Recreated", f"Invoice files for #{self.selected_bill_no} successfully recreated at:\n{pdf_path}")
