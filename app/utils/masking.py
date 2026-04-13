"""
Data masking utilities for sensitive fields.
"""


def mask_aadhaar(aadhaar: str) -> str:
    """
    Mask Aadhaar number — show only last 4 digits.
    e.g. '123456789012' → 'XXXX-XXXX-9012'
    """
    if not aadhaar or len(aadhaar) < 4:
        return "XXXX-XXXX-XXXX"
    cleaned = aadhaar.replace("-", "").replace(" ", "")
    masked = "XXXX-XXXX-" + cleaned[-4:]
    return masked


def mask_pan(pan: str) -> str:
    """
    Mask PAN card — show first 2 and last 2 chars.
    e.g. 'ABCDE1234F' → 'AB******4F'
    """
    if not pan or len(pan) < 4:
        return "**********"
    return pan[:2] + "*" * (len(pan) - 4) + pan[-2:]


def mask_phone(phone: str) -> str:
    """Mask phone — show only last 4 digits."""
    if not phone or len(phone) < 4:
        return "XXXXXX" + phone
    return "XXXXXX" + phone[-4:]
