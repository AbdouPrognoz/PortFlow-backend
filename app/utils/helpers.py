import uuid
from datetime import datetime, timedelta
from typing import Optional
import re


def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()


def calculate_time_difference(start_time: datetime, end_time: datetime) -> timedelta:
    """Calculate the difference between two datetime objects"""
    return end_time - start_time


def sanitize_input(input_str: str) -> str:
    """Basic input sanitization"""
    if input_str:
        # Remove potentially dangerous characters
        sanitized = input_str.strip()
        return sanitized
    return input_str


def generate_qr_payload(booking_id: str, terminal_id: str, timestamp: datetime) -> str:
    """Generate a payload for QR codes"""
    return f"booking:{booking_id}|terminal:{terminal_id}|timestamp:{timestamp.isoformat()}"


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format (basic validation)"""
    # Basic validation: digits, spaces, hyphens, parentheses, plus signs
    pattern = r'^[\+]?[1-9][\d]{0,15}$|^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$'
    return re.match(pattern, phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")) is not None