"""
Email Verification Module
Air Ticket Reservation System

Handles email verification for customer and booking agent registration.
"""

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from flask import url_for, render_template_string
import logging

# Mail instance (will be initialized in app.py)
mail = None
serializer = None

logger = logging.getLogger(__name__)


def init_email_verification(app):
    """
    Initialize email verification system with Flask app.

    Args:
        app: Flask application instance
    """
    global mail, serializer

    # Configure Flask-Mail (update these settings in production)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'your-email@gmail.com'  # Set via environment variable
    app.config['MAIL_PASSWORD'] = 'your-app-password'     # Set via environment variable
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@airticket.com'

    mail = Mail(app)
    serializer = URLSafeTimedSerializer(app.secret_key)

    logger.info('Email verification system initialized')


def generate_verification_token(email):
    """
    Generate a time-limited verification token for an email address.

    Args:
        email: Email address to generate token for

    Returns:
        Verification token string
    """
    return serializer.dumps(email, salt='email-verification')


def verify_token(token, max_age=3600):
    """
    Verify a verification token and extract the email address.

    Args:
        token: Verification token to check
        max_age: Maximum age of token in seconds (default: 1 hour)

    Returns:
        Email address if valid, None if invalid/expired
    """
    try:
        email = serializer.loads(token, salt='email-verification', max_age=max_age)
        return email
    except SignatureExpired:
        logger.warning(f'Verification token expired: {token[:20]}...')
        return None
    except BadSignature:
        logger.warning(f'Invalid verification token: {token[:20]}...')
        return None


def send_verification_email(email, user_type='customer'):
    """
    Send verification email to user.

    Args:
        email: Email address to send to
        user_type: Type of user account ('customer' or 'agent')

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        token = generate_verification_token(email)
        verification_url = url_for('verify_email', token=token, _external=True)

        # Email HTML template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #2a5298;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✈️ Air Ticket System</h1>
                </div>
                <div class="content">
                    <h2>Verify Your Email Address</h2>
                    <p>Thank you for registering as a {user_type}!</p>
                    <p>Please click the button below to verify your email address and activate your account:</p>
                    <p style="text-align: center;">
                        <a href="{verification_url}" class="button">Verify Email Address</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{verification_url}</p>
                    <p><strong>This link will expire in 1 hour.</strong></p>
                    <p>If you didn't create an account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Air Ticket Reservation System</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_body = f"""
        Air Ticket System - Email Verification

        Thank you for registering as a {user_type}!

        Please verify your email address by clicking the link below:
        {verification_url}

        This link will expire in 1 hour.

        If you didn't create an account, please ignore this email.
        """

        msg = Message(
            subject='Verify Your Email - Air Ticket System',
            recipients=[email],
            body=text_body,
            html=html_body
        )

        mail.send(msg)
        logger.info(f'Verification email sent to {email}')
        return True

    except Exception as e:
        logger.error(f'Failed to send verification email to {email}: {str(e)}')
        return False


def send_password_reset_email(email):
    """
    Send password reset email to user.

    Args:
        email: Email address to send to

    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        token = generate_verification_token(email)
        reset_url = url_for('reset_password', token=token, _external=True)

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 5px 5px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #dc3545;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✈️ Air Ticket System</h1>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your password.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{reset_url}</p>
                    <p><strong>This link will expire in 1 hour.</strong></p>
                    <p>If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Air Ticket Reservation System</p>
                    <p>This is an automated message, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg = Message(
            subject='Password Reset - Air Ticket System',
            recipients=[email],
            html=html_body
        )

        mail.send(msg)
        logger.info(f'Password reset email sent to {email}')
        return True

    except Exception as e:
        logger.error(f'Failed to send password reset email to {email}: {str(e)}')
        return False
