<<<<<<< HEAD
# 🛍️ SuperMart - Category-Wise Billing & Inventory Software

A modern, full-featured desktop Point of Sale (POS) and inventory management application built using **Python 3**, **Tkinter GUI**, **SQLite Database**, **ReportLab PDF Exporter**, and **Pillow/QRCode**.

---

## 🌟 Key Features

1. **Category-Wise POS Billing System**:
   - Dynamic category filter buttons (**Toys, Fruits, Dresses, Ice Creams, Groceries, Electronics**).
   - Instant search bar & double-click add-to-cart.
   - Quantity auto-validation against real-time stock levels.
   - Live calculations for Subtotal, Discount, Tax (GST %), and Net Grand Total.
   - Real-time formatted receipt display with dark emerald terminal style.

2. **💳 Customer Details & Payment Checkout Modal**:
   - Popup dialog launched upon clicking **Generate & Payment Bill**.
   - Input and modify Customer Name, Phone, Email, and Billing Address.
   - Select Payment Method (Cash, UPI/QR, Credit Card, Debit Card, Net Banking).
   - Cash Tendered input with instant **Change Due** calculation (`Amount Paid - Net Total`).

3. **⚙️ Dedicated Store & Company Profile Settings Page**:
   - Customize Store / Brand Name, Address, Phone Numbers, Email ID, and GSTIN / Tax ID.
   - Set custom Currency Symbol (`$`, `₹`, `€`, `£`, etc.) and default Tax Rate (GST %).
   - **Manual Logo Upload**: Upload company logo image (`.png`, `.jpg`, `.jpeg`) with live image preview.
   - Changes immediately update the app header banner, text receipts, and PDF invoice headers!

4. **Automated Invoice Generation**:
   - Generates vector **PDF Invoices** with uploaded store logo, store branding, customer details, itemized line items, cash change, and a **UPI Payment QR Code**.
   - Saves plain-text `.txt` copies in the `invoices/` directory.
   - Automatically deducts purchased items from inventory stock upon bill creation.

5. **Product & Stock Inventory Manager (CRUD)**:
   - Complete management for products (Add, Edit, Delete, Search).
   - Assign products to custom categories.
   - Visual warning alerts (`⚠️`) for low-stock items (≤ 5 units).

6. **Category Management (CRUD)**:
   - Create, edit, and delete product categories with descriptions.

7. **Sales & Invoice History Inspector**:
   - View past transactions with customer details and billing dates.
   - Inspect full receipts or re-open/re-generate PDF invoice documents anytime.

8. **Sales Analytics Dashboard**:
   - 4 High-impact KPI Stat cards (Total Revenue, Total Bills, Active Products, Low Stock Count).
   - Category-wise revenue breakdown table and low-stock list.

---

## 🚀 How to Run the Application

### 1. Requirements
- Python 3.10+ (Tested on Python 3.12)
- Required Python Packages:
  ```bash
  pip install reportlab pillow qrcode
  ```

### 2. Launching the Software
Run the following command in your terminal from the project directory:

```bash
python main.py
```
=======
# Billing-
>>>>>>> c08f9e018f97c2b675b113e8e342ea05d48cfce7
