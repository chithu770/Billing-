"""
Store Settings Frame for managing company profile, branding, logo upload, and tax settings.
"""
import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from config import COLORS, FONTS, ASSETS_DIR
from database import fetch_store_settings, update_store_settings

class SettingsFrame(tk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, bg=COLORS["bg_dark"])
        self.app_controller = app_controller
        self.logo_image_tk = None
        self.selected_logo_path = ""

        self._create_widgets()
        self.load_settings()

    def _create_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 1. Header Banner
        hdr_frame = tk.Frame(self, bg=COLORS["bg_card"], padx=15, pady=12, highlightbackground=COLORS["border"], highlightthickness=1)
        hdr_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        tk.Label(hdr_frame, text="⚙️ Company Profile & Store Settings", font=FONTS["title"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(side="left")

        # 2. Main Content Grid (Left: Store Details Form, Right: Logo Upload & Preview)
        content_frame = tk.Frame(self, bg=COLORS["bg_dark"])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.columnconfigure(0, weight=3) # Left Form
        content_frame.columnconfigure(1, weight=2) # Right Logo
        content_frame.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # 2A. LEFT PANEL: Company Details Form
        # ----------------------------------------------------
        form_panel = tk.Frame(content_frame, bg=COLORS["bg_card"], padx=15, pady=15, highlightbackground=COLORS["border"], highlightthickness=1)
        form_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        form_panel.columnconfigure(1, weight=1)

        tk.Label(form_panel, text="🏢 Store Identity & Header Information", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        fields = [
            ("Store / Brand Name:", "shop_name"),
            ("Store Address:", "shop_address"),
            ("Phone Number(s):", "shop_phone"),
            ("Email Address:", "shop_email"),
            ("GSTIN / Tax Registration No:", "shop_gstin"),
            ("Currency Symbol (e.g. $, ₹, €):", "currency_symbol"),
            ("Default Tax Rate (GST %):", "tax_percentage"),
        ]

        self.form_vars = {}
        for idx, (label_text, key) in enumerate(fields, start=1):
            tk.Label(form_panel, text=label_text, font=FONTS["body_bold"], bg=COLORS["bg_card"], fg=COLORS["text_muted"]).grid(row=idx, column=0, sticky="w", pady=6)
            
            var = tk.StringVar()
            entry = tk.Entry(form_panel, textvariable=var, font=FONTS["body"], bg=COLORS["bg_input"], fg=COLORS["text_light"], insertbackground="white", bd=1, relief="solid")
            entry.grid(row=idx, column=1, sticky="ew", pady=6, ipady=3)
            self.form_vars[key] = var

        # Save Button
        btn_save = tk.Button(
            form_panel, text="💾 Save Store Settings", font=FONTS["subtitle"],
            bg=COLORS["success"], fg="white", activebackground=COLORS["success_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=8,
            command=self.save_settings_action
        )
        btn_save.grid(row=len(fields)+1, column=0, columnspan=2, sticky="ew", pady=(20, 0))

        # ----------------------------------------------------
        # 2B. RIGHT PANEL: Company Logo Upload & Preview
        # ----------------------------------------------------
        logo_panel = tk.Frame(content_frame, bg=COLORS["bg_card"], padx=15, pady=15, highlightbackground=COLORS["border"], highlightthickness=1)
        logo_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        logo_panel.columnconfigure(0, weight=1)

        tk.Label(logo_panel, text="🖼️ Company Logo (PDF Header)", font=FONTS["subtitle"], bg=COLORS["bg_card"], fg=COLORS["text_light"]).pack(anchor="w", pady=(0, 15))

        # Logo Preview Box
        self.logo_box = tk.Label(
            logo_panel, text="No Logo Selected\n(Recommended: 300x150 PNG/JPG)",
            font=FONTS["small"], bg=COLORS["bg_input"], fg=COLORS["text_muted"],
            bd=1, relief="solid", width=30, height=8
        )
        self.logo_box.pack(fill="x", pady=(0, 15))

        # Action Buttons
        btn_choose = tk.Button(
            logo_panel, text="📁 Choose Logo Image", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg="white", activebackground=COLORS["primary_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=6,
            command=self.choose_logo_file
        )
        btn_choose.pack(fill="x", pady=(0, 6))

        btn_remove = tk.Button(
            logo_panel, text="❌ Remove Logo", font=FONTS["small"],
            bg=COLORS["danger"], fg="white", activebackground=COLORS["danger_hover"],
            activeforeground="white", relief="flat", cursor="hand2", pady=4,
            command=self.remove_logo_action
        )
        btn_remove.pack(fill="x")

        info_txt = "The selected store logo will automatically appear on the top header of all generated PDF tax invoices."
        tk.Label(logo_panel, text=info_txt, font=FONTS["small"], bg=COLORS["bg_card"], fg=COLORS["text_muted"], wraplength=220, justify="left").pack(anchor="w", pady=(20, 0))

    def load_settings(self):
        settings = fetch_store_settings()
        for key, var in self.form_vars.items():
            var.set(settings.get(key, ""))

        self.selected_logo_path = settings.get("logo_path", "")
        self.display_logo_preview(self.selected_logo_path)

    def display_logo_preview(self, logo_path):
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img.thumbnail((260, 140))
                self.logo_image_tk = ImageTk.PhotoImage(img)
                self.logo_box.config(image=self.logo_image_tk, text="")
                return
            except Exception:
                pass
        
        self.logo_image_tk = None
        self.logo_box.config(image="", text="No Logo Selected\n(Recommended: 300x150 PNG/JPG)")

    def choose_logo_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Store Logo Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("PNG Images", "*.png"), ("JPEG Images", "*.jpg *.jpeg")]
        )
        if not filepath:
            return

        # Save copy to assets dir
        dest_filename = f"logo_{os.path.basename(filepath)}"
        dest_path = os.path.join(ASSETS_DIR, dest_filename)
        try:
            shutil.copy(filepath, dest_path)
            self.selected_logo_path = dest_path
            self.display_logo_preview(self.selected_logo_path)
            messagebox.showinfo("Logo Loaded", "New logo loaded successfully! Click 'Save Store Settings' to apply changes.")
        except Exception as ex:
            messagebox.showerror("Error Copying File", f"Could not save logo image file:\n{ex}")

    def remove_logo_action(self):
        self.selected_logo_path = ""
        self.display_logo_preview("")

    def save_settings_action(self):
        data_to_save = {}
        for key, var in self.form_vars.items():
            val = var.get().strip()
            if key == "tax_percentage":
                try:
                    fval = float(val)
                    if fval < 0:
                        raise ValueError()
                except ValueError:
                    messagebox.showerror("Invalid Tax Rate", "Tax Percentage must be a non-negative number.")
                    return
            data_to_save[key] = val

        data_to_save["logo_path"] = self.selected_logo_path

        try:
            update_store_settings(data_to_save)
            messagebox.showinfo("Settings Saved!", "Store profile & settings updated successfully!")
            self.app_controller.refresh_all_views()
        except Exception as ex:
            messagebox.showerror("Database Error", f"Could not save settings:\n{ex}")
