"""
Logging Configuration
Air Ticket Reservation System

Provides structured logging for security events, user actions, and errors.
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging(app):
    """
    Setup application logging with file rotation.

    Creates three log files:
    - app.log: General application logs
    - security.log: Security-related events
    - error.log: Error-level logs only
    """

    # General application log
    app_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Security log
    security_handler = RotatingFileHandler(
        'logs/security.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Error log
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    # Add handlers to app logger
    app.logger.addHandler(app_handler)
    app.logger.addHandler(security_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    # Don't propagate to root logger
    app.logger.propagate = False

    app.logger.info('Application logging configured')


def log_security_event(event_type, user=None, details=None, ip_address=None):
    """
    Log security-related events.

    Args:
        event_type: Type of event (login_success, login_failed, permission_denied, etc.)
        user: Username or email
        details: Additional details about the event
        ip_address: IP address of the request
    """
    logger = logging.getLogger('security')
    message = f"[{event_type.upper()}] User: {user or 'Anonymous'}"
    if ip_address:
        message += f" | IP: {ip_address}"
    if details:
        message += f" | Details: {details}"

    if event_type in ['login_failed', 'permission_denied', 'unauthorized_access', 'sql_injection_attempt']:
        logger.warning(message)
    else:
        logger.info(message)


def log_user_action(action, user, details=None):
    """
    Log user actions for audit trail.

    Args:
        action: Action performed (ticket_purchase, flight_created, etc.)
        user: Username or email
        details: Additional details
    """
    logger = logging.getLogger('audit')
    message = f"[{action.upper()}] User: {user}"
    if details:
        message += f" | Details: {details}"
    logger.info(message)
