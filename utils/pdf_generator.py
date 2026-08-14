"""
PDF & Text Receipt Generation Module using ReportLab and standard formatting.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from config import INVOICE_DIR
from database import fetch_store_settings
from utils.qr_generator import generate_payment_qr

def get_active_store_settings():
    """Helper to fetch active settings from database with standard defaults."""
    settings = fetch_store_settings()
    return {
        "shop_name": settings.get("shop_name", "SUPERMART HYPERMARKET"),
        "shop_address": settings.get("shop_address", "123 Commercial Avenue, Suite 400, Tech City"),
        "shop_phone": settings.get("shop_phone", "+1 (800) 555-SUPER / +91 9876543210"),
        "shop_email": settings.get("shop_email", "support@supermart.com"),
        "shop_gstin": settings.get("shop_gstin", "33AAAAA0000A1Z5"),
        "currency_symbol": settings.get("currency_symbol", "$"),
        "logo_path": settings.get("logo_path", "")
    }

def generate_text_receipt(bill, items):
    """
    Generates a clean mono-spaced text receipt string for live GUI view & text file saving.
    """
    st = get_active_store_settings()
    currency = st["currency_symbol"]

    lines = []
    lines.append("=" * 48)
    lines.append(f"{st['shop_name']:^48}")
    lines.append(f"{st['shop_address']:^48}")
    lines.append(f"Phone: {st['shop_phone']:^41}")
    lines.append(f"GSTIN: {st['shop_gstin']:^41}")
    lines.append("=" * 48)
    lines.append(f"Bill No   : {bill['bill_no']}")
    lines.append(f"Customer  : {bill['customer_name']}")
    lines.append(f"Phone     : {bill.get('customer_phone') or 'N/A'}")
    if bill.get('customer_email'):
        lines.append(f"Email     : {bill['customer_email']}")
    if bill.get('customer_address'):
        lines.append(f"Address   : {bill['customer_address']}")
    lines.append(f"Date/Time : {bill['date_time']}")
    lines.append("-" * 48)
    lines.append(f"{'Item Name':<20} {'Qty':<4} {'Price':<10} {'Total':<10}")
    lines.append("-" * 48)

    for item in items:
        name = item['product_name'][:19]
        qty = str(item['quantity'])
        price = f"{currency}{item['unit_price']:.2f}"
        total = f"{currency}{item['total_price']:.2f}"
        lines.append(f"{name:<20} {qty:<4} {price:<10} {total:<10}")

    lines.append("-" * 48)
    lines.append(f"{'Subtotal':<34}: {currency}{bill['subtotal']:.2f}")
    lines.append(f"{'Discount':<34}: {currency}{bill['discount_amount']:.2f}")
    lines.append(f"{'Tax (GST)':<34}: {currency}{bill['tax_amount']:.2f}")
    lines.append("=" * 48)
    lines.append(f"{'GRAND TOTAL':<34}: {currency}{bill['net_total']:.2f}")
    if bill.get('amount_paid') and float(bill.get('amount_paid', 0)) > 0:
        lines.append(f"{'Amount Paid':<34}: {currency}{float(bill['amount_paid']):.2f}")
        lines.append(f"{'Change Due':<34}: {currency}{float(bill.get('change_due', 0)):.2f}")
    lines.append("=" * 48)
    lines.append(f"Payment Mode: {bill.get('payment_mode', 'Cash')}")
    lines.append("")
    lines.append(f"{'Thank you for shopping with us!':^48}")
    lines.append(f"{'Please Visit Again':^48}")
    lines.append("=" * 48)
    
    receipt_str = "\n".join(lines)
    
    # Save .txt copy
    txt_filename = os.path.join(INVOICE_DIR, f"{bill['bill_no']}.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(receipt_str)

    return receipt_str

def generate_pdf_invoice(bill, items):
    """
    Generates a professional PDF invoice document using ReportLab.
    Returns file path of the generated PDF.
    """
    st = get_active_store_settings()
    currency = st["currency_symbol"]

    pdf_filename = os.path.join(INVOICE_DIR, f"{bill['bill_no']}.pdf")
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1e1b4b')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569')
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#6366f1')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # 1. Store Header Table (Logo Image + Store Metadata + Invoice Title)
    logo_flowable = None
    if st["logo_path"] and os.path.exists(st["logo_path"]):
        try:
            logo_flowable = Image(st["logo_path"], width=1.5 * inch, height=0.75 * inch)
        except Exception:
            logo_flowable = None

    store_text_content = f"<b>{st['shop_name']}</b><br/>{st['shop_address']}<br/>Phone: {st['shop_phone']} | Email: {st['shop_email']}<br/>GSTIN: {st['shop_gstin']}"
    
    if logo_flowable:
        header_data = [
            [
                logo_flowable,
                Paragraph(store_text_content, subtitle_style),
                Paragraph(f"<b>TAX INVOICE</b><br/><font color='#6366f1'><b>#{bill['bill_no']}</b></font><br/>Date: {bill['date_time']}", title_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[1.6 * inch, 2.7 * inch, 2.7 * inch])
    else:
        header_data = [
            [
                Paragraph(store_text_content, subtitle_style),
                Paragraph(f"<b>TAX INVOICE</b><br/><font color='#6366f1'><b>#{bill['bill_no']}</b></font><br/>Date: {bill['date_time']}", title_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[3.5 * inch, 3.5 * inch])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (-1,0), (-1,0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#6366f1'), spaceAfter=12))

    # 2. Customer Information Card
    cust_details_str = f"Customer: <b>{bill['customer_name']}</b><br/>Phone: {bill.get('customer_phone') or 'N/A'}"
    if bill.get('customer_email'):
        cust_details_str += f"<br/>Email: {bill['customer_email']}"
    if bill.get('customer_address'):
        cust_details_str += f"<br/>Address: {bill['customer_address']}"

    cust_info = [
        [
            Paragraph(f"<b>Billed To:</b><br/>{cust_details_str}", subtitle_style),
            Paragraph(f"<b>Payment Details:</b><br/>Mode: <b>{bill.get('payment_mode', 'Cash')}</b><br/>Status: <b>PAID</b>", subtitle_style)
        ]
    ]
    cust_table = Table(cust_info, colWidths=[3.5 * inch, 3.5 * inch])
    cust_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 15))

    # 3. Product Line Items Table
    table_data = [
        [
            Paragraph("S.No", table_header_style),
            Paragraph("Item & Category", table_header_style),
            Paragraph("Unit Price", table_header_style),
            Paragraph("Qty", table_header_style),
            Paragraph("Total Amount", table_header_style),
        ]
    ]

    for idx, item in enumerate(items, 1):
        table_data.append([
            Paragraph(str(idx), table_cell_style),
            Paragraph(f"<b>{item['product_name']}</b><br/><font color='#64748b'>Category: {item['category_name']}</font>", table_cell_style),
            Paragraph(f"{currency}{item['unit_price']:.2f}", table_cell_style),
            Paragraph(str(item['quantity']), table_cell_style),
            Paragraph(f"<b>{currency}{item['total_price']:.2f}</b>", table_cell_style),
        ])

    items_table = Table(table_data, colWidths=[0.5 * inch, 3.3 * inch, 1.1 * inch, 0.7 * inch, 1.4 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e1b4b')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))

    # 4. Summary & QR Code Section
    qr_img_path = generate_payment_qr(bill['net_total'], bill['bill_no'])
    qr_image = Image(qr_img_path, width=1.1 * inch, height=1.1 * inch)

    calc_rows = [
        [Paragraph("Subtotal:", table_cell_style), Paragraph(f"{currency}{bill['subtotal']:.2f}", table_cell_style)],
        [Paragraph("Discount:", table_cell_style), Paragraph(f"- {currency}{bill['discount_amount']:.2f}", table_cell_style)],
        [Paragraph("Tax (GST):", table_cell_style), Paragraph(f"+ {currency}{bill['tax_amount']:.2f}", table_cell_style)],
        [Paragraph("<b>GRAND TOTAL:</b>", h2_style), Paragraph(f"<b><font color='#6366f1' size=14>{currency}{bill['net_total']:.2f}</font></b>", h2_style)],
    ]

    if bill.get('amount_paid') and float(bill.get('amount_paid', 0)) > 0:
        calc_rows.append([Paragraph("Amount Paid:", table_cell_style), Paragraph(f"{currency}{float(bill['amount_paid']):.2f}", table_cell_style)])
        calc_rows.append([Paragraph("Change Due:", table_cell_style), Paragraph(f"{currency}{float(bill.get('change_due', 0)):.2f}", table_cell_style)])

    summary_data = [
        [
            qr_image,
            Paragraph("<b>Scan QR code with any UPI app to make payment & verify digital invoice receipt.</b>", subtitle_style),
            Table(calc_rows, colWidths=[1.4 * inch, 1.4 * inch])
        ]
    ]

    summary_table = Table(summary_data, colWidths=[1.2 * inch, 2.5 * inch, 3.3 * inch])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # 5. Footer Terms & Thank you note
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    story.append(Paragraph("<b>Terms & Conditions:</b> Goods once sold will not be taken back without original receipt. Warranty claims as per manufacturer policy.", subtitle_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Thank you for shopping at {st['shop_name']}!</b>", ParagraphStyle('Thanks', parent=subtitle_style, fontName='Helvetica-Bold', alignment=1, fontSize=11, textColor=colors.HexColor('#1e1b4b'))))

    doc.build(story)
    return pdf_filename
