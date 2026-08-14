"""
Category Management Frame (CRUD) for managing product categories.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS
from database import (
    fetch_all_categories, add_category, 
    update_category, delete_category, fetch_all_products
)

class CategoriesFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller
        self.selected_cat_id = None
        self.selected_cat_name = None

        self._create_widgets()
        self.load_categories()

    def _create_widgets(self):
        self.columnconfigure(0, weight=3) # Left: Categories list
        self.columnconfigure(1, weight=2) # Right: Form
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 1. LEFT PANEL: Categories Table
        # ----------------------------------------------------
        left_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)

        hdr = tk.Label(left_panel, text="🏷️ Category Management", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        table_frame = tk.Frame(left_panel, bg=COLORS["bg_card"])
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        columns = ("id", "name", "desc", "prod_count")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Category Name")
        self.tree.heading("desc", text="Description")
        self.tree.heading("prod_count", text="Assigned Products")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=140, anchor="w")
        self.tree.column("desc", width=220, anchor="w")
        self.tree.column("prod_count", width=110, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<<TreeviewSelect>>", self.on_category_select)

        # ----------------------------------------------------
        # 2. RIGHT PANEL: Category Details Form
        # ----------------------------------------------------
        right_panel = tk.Frame(self, bg=COLORS["bg_card"], padx=12, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_panel.columnconfigure(1, weight=1)

        form_hdr = tk.Label(right_panel, text="✏️ Category Details Form", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"], anchor="w")
        form_hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        tk.Label(right_panel, text="Category Name:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar()
        name_ent = tk.Entry(right_panel, textvariable=self.name_var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
        name_ent.grid(row=1, column=1, sticky="ew", pady=6, ipady=3)

        tk.Label(right_panel, text="Description:", font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=2, column=0, sticky="nw", pady=6)
        self.desc_txt = tk.Text(right_panel, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid", height=5)
        self.desc_txt.grid(row=2, column=1, sticky="ew", pady=6)

        # Buttons
        btn_box = tk.Frame(right_panel, bg=COLORS["bg_card"], pady=15)
        btn_box.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.btn_save = tk.Button(
            btn_box, text="➕ Add Category", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            command=self.save_category
        )
        self.btn_save.pack(fill="x", pady=(0, 6))

        self.btn_update = tk.Button(
            btn_box, text="💾 Update Category", font=FONTS["body_bold"],
            bg=COLORS["secondary"], fg="white", activebackground=COLORS["secondary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.update_category_action
        )
        self.btn_update.pack(fill="x", pady=(0, 6))

        self.btn_delete = tk.Button(
            btn_box, text="🗑️ Delete Category", font=FONTS["body_bold"],
            bg=COLORS["danger"], fg="white", activebackground=COLORS["danger_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            state="disabled", command=self.delete_category_action
        )
        self.btn_delete.pack(fill="x", pady=(0, 6))

        btn_clear = tk.Button(
            btn_box, text="🔄 Clear Form", font=FONTS["body"],
            bg=COLORS["bg_card_alt"], fg=COLORS["text_light"], relief="flat", cursor="hand2", pady=4,
            command=self.clear_form
        )
        btn_clear.pack(fill="x")

    def load_categories(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = fetch_all_categories()
        all_products = fetch_all_products()

        for c in categories:
            prod_count = len([p for p in all_products if p["category_name"] == c["name"]])
            self.tree.insert("", "end", iid=str(c["id"]), values=(
                c["id"], c["name"], c["description"] or "", prod_count
            ))

    def on_category_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        cat_id = int(selected[0])
        categories = fetch_all_categories()
        cat = next((c for c in categories if c["id"] == cat_id), None)
        if not cat:
            return

        self.selected_cat_id = cat_id
        self.selected_cat_name = cat["name"]
        self.name_var.set(cat["name"])
        self.desc_txt.delete("1.0", tk.END)
        if cat["description"]:
            self.desc_txt.insert(tk.END, cat["description"])

        self.btn_save.config(state="disabled")
        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")

    def clear_form(self):
        self.selected_cat_id = None
        self.selected_cat_name = None
        self.name_var.set("")
        self.desc_txt.delete("1.0", tk.END)
        self.tree.selection_remove(self.tree.selection())

        self.btn_save.config(state="normal")
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")

    def save_category(self):
        name = self.name_var.get().strip()
        desc = self.desc_txt.get("1.0", tk.END).strip()

        if not name:
            messagebox.showwarning("Validation Error", "Category Name is required.")
            return

        try:
            add_category(name, desc)
            messagebox.showinfo("Success", f"Category '{name}' created successfully!")
            self.clear_form()
            self.load_categories()
            self.app_controller.refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Database Error", f"Could not create category:\n{ex}")

    def update_category_action(self):
        if not self.selected_cat_id:
            return

        name = self.name_var.get().strip()
        desc = self.desc_txt.get("1.0", tk.END).strip()

        if not name:
            messagebox.showwarning("Validation Error", "Category Name is required.")
            return

        try:
            update_category(self.selected_cat_id, name, desc, self.selected_cat_name)
            messagebox.showinfo("Success", f"Category '{name}' updated successfully!")
            self.clear_form()
            self.load_categories()
            self.app_controller.refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Database Error", f"Could not update category:\n{ex}")

    def delete_category_action(self):
        if not self.selected_cat_id or not self.selected_cat_name:
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete category '{self.selected_cat_name}'?"):
            try:
                delete_category(self.selected_cat_id, self.selected_cat_name)
                messagebox.showinfo("Deleted", "Category removed successfully.")
                self.clear_form()
                self.load_categories()
                self.app_controller.refresh_all_views()
            except Exception as ex:
                messagebox.showerror("Cannot Delete Category", str(ex))
