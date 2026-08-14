"""
Main Application Window container & navigation controller.
"""
import datetime
import tkinter as tk
from tkinter import ttk
from config import APP_TITLE, COLORS, FONTS
from database import init_db, fetch_store_settings
from gui.billing_frame import BillingFrame
from gui.products_frame import ProductsFrame
from gui.categories_frame import CategoriesFrame
from gui.history_frame import HistoryFrame
from gui.dashboard_frame import DashboardFrame
from gui.settings_frame import SettingsFrame

class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(APP_TITLE)
        self.geometry("1380x780")
        self.minsize(1150, 680)
        self.configure(bg=COLORS["bg_dark"])

        # High DPI Awareness on Windows
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Initialize Database
        init_db()

        # Apply Custom Modern TTK Styles
        self._configure_styles()

        # Build UI Structure
        self._create_header()
        self._create_navbar()
        self._create_container()
        self._create_statusbar()

        # Instantiate Sub-Frames
        self.frames = {}
        self.current_frame_name = None

        frame_classes = {
            "billing": BillingFrame,
            "products": ProductsFrame,
            "categories": CategoriesFrame,
            "history": HistoryFrame,
            "dashboard": DashboardFrame,
            "settings": SettingsFrame,
        }

        for name, cls in frame_classes.items():
            frame = cls(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show initial frame
        self.show_frame("billing")

        # Start live clock timer
        self._update_clock()
        self._update_header_branding()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure Treeview (Dark Theme)
        style.configure(
            "Treeview",
            background=COLORS["bg_card"],
            foreground=COLORS["text_light"],
            fieldbackground=COLORS["bg_card"],
            rowheight=28,
            font=FONTS["body"]
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["header_bg"],
            foreground=COLORS["text_light"],
            font=FONTS["header"],
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["primary"])],
            foreground=[("selected", "white")]
        )
        style.map(
            "Treeview.Heading",
            background=[("active", COLORS["primary_hover"])]
        )

        # Configure Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=COLORS["bg_card_alt"],
            troughcolor=COLORS["bg_dark"],
            bordercolor=COLORS["bg_dark"],
            arrowcolor=COLORS["text_muted"]
        )

        # Configure Combobox
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["bg_input"],
            background=COLORS["bg_card_alt"],
            foreground=COLORS["text_light"],
            font=FONTS["body"]
        )

    def _create_header(self):
        hdr_frame = tk.Frame(self, bg=COLORS["header_bg"], padx=15, pady=10)
        hdr_frame.pack(side="top", fill="x")

        # Shop Brand Info
        self.brand_lbl = tk.Label(hdr_frame, font=FONTS["title"], bg=COLORS["header_bg"], fg="white")
        self.brand_lbl.pack(side="left")

        self.sub_lbl = tk.Label(hdr_frame, font=FONTS["small"], bg=COLORS["header_bg"], fg=COLORS["text_muted"])
        self.sub_lbl.pack(side="left", pady=(3, 0))

        # Live Clock
        self.lbl_clock = tk.Label(hdr_frame, font=FONTS["header"], bg=COLORS["header_bg"], fg=COLORS["success"])
        self.lbl_clock.pack(side="right")

    def _create_navbar(self):
        nav_frame = tk.Frame(self, bg=COLORS["bg_card"], padx=10, pady=6, highlightbackground=COLORS["border"], highlightthickness=1)
        nav_frame.pack(side="top", fill="x")

        nav_buttons = [
            ("🛒 Billing POS", "billing"),
            ("📦 Product Inventory", "products"),
            ("🏷️ Categories", "categories"),
            ("📜 Sales History", "history"),
            ("📊 Dashboard & Stats", "dashboard"),
            ("⚙️ Store Settings", "settings"),
        ]

        self.nav_btns = {}
        for text, frame_name in nav_buttons:
            btn = tk.Button(
                nav_frame, text=text, font=FONTS["header"],
                bg=COLORS["bg_card_alt"], fg=COLORS["text_light"],
                activebackground=COLORS["primary"], activeforeground="white",
                relief="flat", cursor="hand2", padx=15, pady=6,
                command=lambda f=frame_name: self.show_frame(f)
            )
            btn.pack(side="left", padx=4)
            self.nav_btns[frame_name] = btn

    def _create_container(self):
        self.container = tk.Frame(self, bg=COLORS["bg_dark"])
        self.container.pack(side="top", fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

    def _create_statusbar(self):
        status_frame = tk.Frame(self, bg=COLORS["header_bg"], padx=10, pady=4)
        status_frame.pack(side="bottom", fill="x")

        self.lbl_status = tk.Label(status_frame, text="🟢 System Online | Database Connected (billing_database.db)", font=FONTS["small"], bg=COLORS["header_bg"], fg=COLORS["text_muted"])
        self.lbl_status.pack(side="left")

        ver_lbl = tk.Label(status_frame, text="SuperMart POS v2.0.0", font=FONTS["small"], bg=COLORS["header_bg"], fg=COLORS["text_muted"])
        ver_lbl.pack(side="right")

    def _update_header_branding(self):
        st = fetch_store_settings()
        shop_name = st.get("shop_name", "SUPERMART HYPERMARKET")
        gstin = st.get("shop_gstin", "33AAAAA0000A1Z5")

        self.brand_lbl.config(text=f"🛍️ {shop_name}")
        self.sub_lbl.config(text=f"  |  Category-Wise Billing & Inventory System  (GSTIN: {gstin})")

    def show_frame(self, frame_name):
        """Switches visible active frame and highlights navbar button."""
        frame = self.frames.get(frame_name)
        if frame:
            frame.tkraise()
            self.current_frame_name = frame_name

            # Highlight active navbar button
            for name, btn in self.nav_btns.items():
                if name == frame_name:
                    btn.config(bg=COLORS["primary"], fg="white")
                else:
                    btn.config(bg=COLORS["bg_card_alt"], fg=COLORS["text_light"])

    def refresh_all_views(self):
        """Notifies all frames to reload data when updates occur."""
        self._update_header_branding()
        for name, frame in self.frames.items():
            if hasattr(frame, "load_settings"):
                frame.load_settings()
            if hasattr(frame, "load_categories"):
                frame.load_categories()
            if hasattr(frame, "load_categories_combo"):
                frame.load_categories_combo()
            if hasattr(frame, "load_products"):
                frame.load_products()
            if hasattr(frame, "load_bills"):
                frame.load_bills()
            if hasattr(frame, "load_dashboard_data"):
                frame.load_dashboard_data()

    def _update_clock(self):
        now_str = datetime.datetime.now().strftime("%A, %b %d %Y | %I:%M:%S %p")
        self.lbl_clock.config(text=f"🕒 {now_str}")
        self.after(1000, self._update_clock)
