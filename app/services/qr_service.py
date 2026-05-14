import qrcode
import io
import base64
from datetime import datetime
import hashlib
import json

def generate_qr_code(leave_id):
    """Generate QR code for approved leave"""
    # Create data for QR code - simple format that can be validated
    qr_data = f"LEAVE-{leave_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Convert to image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 string
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def validate_qr_code(qr_code):
    """Validate QR code and extract leave ID"""
    try:
        # Check if it's a valid format
        if not qr_code or not isinstance(qr_code, str):
            return None
            
        # Check if it matches our format: LEAVE-{id}-{timestamp}
        parts = qr_code.split('-')
        if len(parts) >= 2 and parts[0] == 'LEAVE':
            try:
                leave_id = int(parts[1])
                return leave_id
            except ValueError:
                return None
    except Exception as e:
        print(f"QR validation error: {e}")
    
    return None
