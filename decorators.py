"""
Route Decorators for Access Control
Air Ticket Reservation System

These decorators ensure that only authorized users can access protected routes.
They check session data before allowing access to the wrapped function.
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Ensure user is logged in before accessing the route.
    Redirects to login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def customer_required(f):
    """
    Ensure the logged-in user is a customer.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'customer':
            flash('Access denied. Customer account required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def agent_required(f):
    """
    Ensure the logged-in user is a booking agent.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'agent':
            flash('Access denied. Booking agent account required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def staff_required(f):
    """
    Ensure the logged-in user is airline staff.
    Must be used after @login_required.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'staff':
            flash('Access denied. Airline staff account required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Ensure the logged-in staff member has Admin permission.
    Must be used after @staff_required.
    
    Admin can: Add airports, airplanes, create flights, associate booking agents.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'staff':
            flash('Access denied. Staff account required.', 'error')
            return redirect(url_for('index'))
        
        permissions = session.get('permissions', [])
        if 'Admin' not in permissions:
            flash('Access denied. Admin permission required.', 'error')
            return redirect(url_for('staff_home'))
        return f(*args, **kwargs)
    return decorated_function


def operator_required(f):
    """
    Ensure the logged-in staff member has Operator permission.
    Must be used after @staff_required.
    
    Operator can: Update flight status.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'staff':
            flash('Access denied. Staff account required.', 'error')
            return redirect(url_for('index'))
        
        permissions = session.get('permissions', [])
        if 'Operator' not in permissions:
            flash('Access denied. Operator permission required.', 'error')
            return redirect(url_for('staff_home'))
        return f(*args, **kwargs)
    return decorated_function


def admin_or_operator_required(f):
    """
    Ensure the logged-in staff member has either Admin or Operator permission.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'staff':
            flash('Access denied. Staff account required.', 'error')
            return redirect(url_for('index'))
        
        permissions = session.get('permissions', [])
        if 'Admin' not in permissions and 'Operator' not in permissions:
            flash('Access denied. Admin or Operator permission required.', 'error')
            return redirect(url_for('staff_home'))
        return f(*args, **kwargs)
    return decorated_function
