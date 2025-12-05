"""
Security Utilities
Air Ticket Reservation System

This module provides:
- Password hashing and verification
- Input validation and sanitization
- Protection against common attacks
"""

import hashlib
import re
from datetime import datetime


# ========== PASSWORD HASHING ==========

def hash_password(password):
    """
    Hash a password using SHA-256.
    
    For production, consider using bcrypt or argon2 instead:
        from werkzeug.security import generate_password_hash
        return generate_password_hash(password)
    
    Args:
        password: Plain text password
    
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password, hashed):
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password to check
        hashed: Stored hash to compare against
    
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(password) == hashed


# ========== INPUT SANITIZATION ==========

def sanitize_string(value, max_length=255, min_length=None, field_name=None, raise_on_error=False):
    """
    Sanitize a string input by stripping whitespace and validating length.

    Args:
        value: Input value (can be None)
        max_length: Maximum allowed length
        min_length: Minimum required length (optional)
        field_name: Name of field for error messages
        raise_on_error: If True, raise ValueError instead of returning None

    Returns:
        Sanitized string or None

    Raises:
        ValueError: If raise_on_error=True and validation fails
    """
    if value is None:
        return None

    value = str(value).strip()

    if len(value) == 0:
        return None

    # Check minimum length
    if min_length and len(value) < min_length:
        if raise_on_error:
            field = field_name or "Input"
            raise ValueError(f"{field} must be at least {min_length} characters")
        return None

    # Check maximum length
    if len(value) > max_length:
        if raise_on_error:
            field = field_name or "Input"
            raise ValueError(f"{field} exceeds maximum length of {max_length} characters")
        # Silently truncate if not raising errors (backward compatible)
        return value[:max_length]

    return value


def sanitize_int(value, default=None, min_val=None, max_val=None):
    """
    Safely convert input to integer with bounds checking.
    
    Args:
        value: Input value to convert
        default: Default value if conversion fails
        min_val: Minimum allowed value (optional)
        max_val: Maximum allowed value (optional)
    
    Returns:
        Integer value or default
    """
    try:
        result = int(value)
        if min_val is not None and result < min_val:
            return default
        if max_val is not None and result > max_val:
            return default
        return result
    except (ValueError, TypeError):
        return default


def sanitize_float(value, default=None, min_val=None, max_val=None):
    """
    Safely convert input to float with bounds checking.
    """
    try:
        result = float(value)
        if min_val is not None and result < min_val:
            return default
        if max_val is not None and result > max_val:
            return default
        return result
    except (ValueError, TypeError):
        return default


# ========== INPUT VALIDATION ==========

def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email string to validate
    
    Returns:
        True if valid email format, False otherwise
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_date(date_str):
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid date format, False otherwise
    """
    if not date_str:
        return False
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    # Also check if it's a valid date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_datetime(datetime_str):
    """
    Validate datetime format (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM).
    
    Args:
        datetime_str: Datetime string to validate
    
    Returns:
        True if valid datetime format, False otherwise
    """
    if not datetime_str:
        return False
    
    formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%dT%H:%M']
    for fmt in formats:
        try:
            datetime.strptime(datetime_str, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_time(time_str):
    """
    Validate time format (HH:MM or HH:MM:SS).
    """
    if not time_str:
        return False
    patterns = [r'^\d{2}:\d{2}$', r'^\d{2}:\d{2}:\d{2}$']
    return any(re.match(p, time_str) for p in patterns)


def validate_positive_int(value):
    """
    Check if value is a positive integer.
    
    Args:
        value: Value to check
    
    Returns:
        True if positive integer, False otherwise
    """
    try:
        return int(value) > 0
    except (ValueError, TypeError):
        return False


def validate_non_negative_float(value):
    """
    Check if value is a non-negative number.
    """
    try:
        return float(value) >= 0
    except (ValueError, TypeError):
        return False


def validate_phone(phone):
    """
    Validate phone number format (allows various formats).
    """
    if not phone:
        return False
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if remaining is digits and reasonable length
    return cleaned.isdigit() and 7 <= len(cleaned) <= 15


def validate_alphanumeric(value, allow_spaces=False, allow_underscore=False):
    """
    Check if value contains only alphanumeric characters.
    """
    if not value:
        return False
    pattern = r'^[a-zA-Z0-9'
    if allow_spaces:
        pattern += r'\s'
    if allow_underscore:
        pattern += r'_'
    pattern += r']+$'
    return re.match(pattern, value) is not None


def validate_in_list(value, allowed_values):
    """
    Check if value is in a list of allowed values.
    
    Args:
        value: Value to check
        allowed_values: List of allowed values
    
    Returns:
        True if value is in allowed_values, False otherwise
    """
    return value in allowed_values


# ========== FLIGHT STATUS VALIDATION ==========

ALLOWED_FLIGHT_STATUSES = ['Upcoming', 'In-Progress', 'Delayed', 'Completed', 'Cancelled']

def validate_flight_status(status):
    """Validate that status is one of the allowed flight statuses."""
    return status in ALLOWED_FLIGHT_STATUSES


# ========== PASSWORD STRENGTH ==========

def validate_password_strength(password, min_length=6):
    """
    Check if password meets minimum requirements.
    
    Args:
        password: Password to check
        min_length: Minimum required length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    return True, None
