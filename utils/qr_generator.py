"""
QR Code Generator for UPI payment and digital receipt validation.
"""
import os
import qrcode
from config import ASSETS_DIR, SHOP_NAME

def generate_payment_qr(amount, bill_no, upi_id="supermart@upi"):
    """
    Generates a UPI Payment QR code image for the specified amount and bill number.
    Returns the file path of the generated PNG.
    """
    qr_filename = f"qr_{bill_no}.png"
    qr_path = os.path.join(ASSETS_DIR, qr_filename)
    
    # Standard UPI URI scheme
    upi_url = f"upi://pay?pa={upi_id}&pn={SHOP_NAME.replace(' ', '%20')}&am={amount:.2f}&tn=Bill%20{bill_no}&cu=USD"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=2,
    )
    qr.add_data(upi_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e1b4b", back_color="white")
    img.save(qr_path)
    return qr_path
