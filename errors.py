"""
Error Messages and Constants
Air Ticket Reservation System

Centralized error messages for consistency across the application.
"""

# Authentication Errors
AUTH_ERRORS = {
    'login_required': 'Please log in to access this page.',
    'invalid_credentials': 'Invalid username/email or password.',
    'account_locked': 'Your account has been locked due to multiple failed login attempts. Please try again later.',
    'session_expired': 'Your session has expired. Please log in again.',
}

# Validation Errors
VALIDATION_ERRORS = {
    'required_field': '{field} is required.',
    'invalid_email': 'Please enter a valid email address.',
    'invalid_date': 'Please enter a valid date in YYYY-MM-DD format.',
    'invalid_datetime': 'Please enter a valid date and time.',
    'password_mismatch': 'Passwords do not match.',
    'password_too_short': 'Password must be at least {min_length} characters.',
    'password_too_weak': 'Password must contain at least one uppercase letter, one lowercase letter, and one number.',
    'invalid_phone': 'Please enter a valid phone number.',
    'field_too_long': '{field} exceeds maximum length of {max_length} characters.',
    'field_too_short': '{field} must be at least {min_length} characters.',
    'invalid_number': 'Please enter a valid number.',
    'negative_number': '{field} cannot be negative.',
}

# Business Logic Errors
BUSINESS_ERRORS = {
    'flight_full': 'Sorry, this flight is fully booked.',
    'flight_not_available': 'Flight not found or no longer available for booking.',
    'past_flight': 'Cannot book a flight in the past.',
    'same_airports': 'Departure and arrival airports must be different.',
    'insufficient_seats': 'Not enough seats available.',
    'already_purchased': 'You have already purchased a ticket for this flight.',
}

# Success Messages
SUCCESS_MESSAGES = {
    'login_success': 'Welcome back, {name}!',
    'logout_success': 'You have been logged out successfully.',
    'registration_success': 'Registration successful! Please log in.',
    'ticket_purchased': 'Ticket purchased successfully!',
    'flight_created': 'Flight added successfully!',
    'airplane_added': 'Airplane added successfully!',
    'airport_added': 'Airport added successfully!',
    'agent_associated': 'Booking agent associated successfully!',
    'status_updated': 'Flight status updated successfully.',
    'profile_updated': 'Profile updated successfully.',
}


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Custom exception for authorization errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Custom exception for business logic errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def format_error(error_key, **kwargs):
    """
    Format an error message with parameters.

    Args:
        error_key: Key from error dictionaries
        **kwargs: Parameters to format the message

    Returns:
        Formatted error message
    """
    # Search through all error dictionaries
    for error_dict in [AUTH_ERRORS, VALIDATION_ERRORS, BUSINESS_ERRORS]:
        if error_key in error_dict:
            return error_dict[error_key].format(**kwargs)

    # Return the key itself if not found
    return error_key


def format_success(success_key, **kwargs):
    """
    Format a success message with parameters.

    Args:
        success_key: Key from SUCCESS_MESSAGES
        **kwargs: Parameters to format the message

    Returns:
        Formatted success message
    """
    if success_key in SUCCESS_MESSAGES:
        return SUCCESS_MESSAGES[success_key].format(**kwargs)
    return success_key
