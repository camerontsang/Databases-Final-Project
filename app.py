"""
Air Ticket Reservation System - Main Application
CSCI-SHU 213 Project Part 3

This Flask application implements a secure air ticket reservation system
with four user types: Public, Customer, Booking Agent, and Airline Staff.
"""

from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from config import execute_query, SECRET_KEY
from security import (
    hash_password, verify_password, sanitize_string, sanitize_int, sanitize_float,
    validate_email, validate_date, validate_datetime, validate_positive_int,
    validate_password_strength, validate_flight_status, ALLOWED_FLIGHT_STATUSES
)
from decorators import (
    login_required, customer_required, agent_required,
    staff_required, admin_required, operator_required
)
from logging_config import setup_logging, log_security_event, log_user_action
from errors import (
    AUTH_ERRORS, VALIDATION_ERRORS, BUSINESS_ERRORS, SUCCESS_MESSAGES,
    format_error, format_success
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Setup logging
setup_logging(app)

# Setup CSRF protection (disabled by default - enable after updating templates)
# To enable: Set WTF_CSRF_ENABLED = True and add csrf_token() to all forms
app.config['WTF_CSRF_ENABLED'] = False  # Temporarily disabled
csrf = CSRFProtect(app)

# Setup rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

app.logger.info('Application initialized with CSRF protection disabled (update templates to enable)')

# ============================================================================
# CONTEXT PROCESSORS - Make variables available to all templates
# ============================================================================

@app.context_processor
def inject_user():
    """Inject user info into all templates"""
    return {
        'logged_in': 'user' in session,
        'user_type': session.get('user_type'),
        'username': session.get('user'),
        'user_name': session.get('name'),
        'airline': session.get('airline'),
        'permissions': session.get('permissions', [])
    }


# ============================================================================
# PUBLIC ROUTES - Accessible without login
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('public/index.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")  # Rate limit: 10 login attempts per minute
def login():
    """Handle user login for all user types"""
    if 'user' in session:
        # Already logged in, redirect to appropriate home
        return redirect_to_home()

    if request.method == 'POST':
        username = sanitize_string(request.form.get('username'))
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        # Validate inputs
        if not username or not password or not user_type:
            flash('Please fill in all fields.', 'error')
            return render_template('public/login.html')

        hashed_pw = hash_password(password)

        # Authenticate based on user type
        if user_type == 'customer':
            user = execute_query(
                "SELECT * FROM customer WHERE email = %s AND password = %s",
                (username, hashed_pw), fetch_one=True
            )
            if user:
                session['user'] = user['email']
                session['user_type'] = 'customer'
                session['name'] = user['name']
                log_security_event('login_success', user=username, ip_address=request.remote_addr)
                log_user_action('login', username, f'Logged in as customer')
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('customer_home'))

        elif user_type == 'agent':
            user = execute_query(
                "SELECT * FROM booking_agent WHERE email = %s AND password = %s",
                (username, hashed_pw), fetch_one=True
            )
            if user:
                session['user'] = user['email']
                session['user_type'] = 'agent'
                session['agent_id'] = user['booking_agent_id']
                log_security_event('login_success', user=username, ip_address=request.remote_addr)
                log_user_action('login', username, f'Logged in as booking agent')
                flash('Welcome back!', 'success')
                return redirect(url_for('agent_home'))

        elif user_type == 'staff':
            user = execute_query(
                "SELECT * FROM airline_staff WHERE username = %s AND password = %s",
                (username, hashed_pw), fetch_one=True
            )
            if user:
                session['user'] = user['username']
                session['user_type'] = 'staff'
                session['airline'] = user['airline_name']
                session['name'] = user['first_name'] + ' ' + user['last_name']

                # Get staff permissions
                permissions = execute_query(
                    "SELECT permission_type FROM permission WHERE username = %s",
                    (username,)
                )
                session['permissions'] = [p['permission_type'] for p in permissions]

                log_security_event('login_success', user=username, ip_address=request.remote_addr)
                log_user_action('login', username, f'Logged in as staff for {user["airline_name"]}')
                flash(f'Welcome back, {user["first_name"]}!', 'success')
                return redirect(url_for('staff_home'))

        # Failed login attempt
        log_security_event('login_failed', user=username, details=f'Failed {user_type} login', ip_address=request.remote_addr)
        flash('Invalid username/email or password.', 'error')

    return render_template('public/login.html')


@app.route('/logout')
def logout():
    """Log out the current user"""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET'])
def register_select():
    """Show registration type selection"""
    return render_template('public/register_select.html')


@app.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    """Customer registration"""
    if request.method == 'POST':
        # Get and sanitize all inputs
        email = sanitize_string(request.form.get('email'))
        name = sanitize_string(request.form.get('name'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        building_number = sanitize_string(request.form.get('building_number'))
        street = sanitize_string(request.form.get('street'))
        city = sanitize_string(request.form.get('city'))
        state = sanitize_string(request.form.get('state'))
        phone_number = sanitize_string(request.form.get('phone_number'))
        passport_number = sanitize_string(request.form.get('passport_number'))
        passport_expiration = sanitize_string(request.form.get('passport_expiration'))
        passport_country = sanitize_string(request.form.get('passport_country'))
        date_of_birth = sanitize_string(request.form.get('date_of_birth'))
        
        # Validate required fields
        errors = []
        if not email or not validate_email(email):
            errors.append('Valid email is required.')
        if not name:
            errors.append('Name is required.')
        
        # Validate password
        is_valid, pwd_error = validate_password_strength(password)
        if not is_valid:
            errors.append(pwd_error)
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Validate dates
        if passport_expiration and not validate_date(passport_expiration):
            errors.append('Invalid passport expiration date format.')
        if date_of_birth and not validate_date(date_of_birth):
            errors.append('Invalid date of birth format.')
        
        # Check if email already exists
        existing = execute_query(
            "SELECT email FROM customer WHERE email = %s",
            (email,), fetch_one=True
        )
        if existing:
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('public/register_customer.html')
        
        # Insert new customer
        hashed_pw = hash_password(password)
        try:
            execute_query(
                """INSERT INTO customer 
                   (email, name, password, building_number, street, city, state, 
                    phone_number, passport_number, passport_expiration, passport_country, date_of_birth)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (email, name, hashed_pw, building_number, street, city, state,
                 phone_number, passport_number, passport_expiration, passport_country, date_of_birth),
                commit=True
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('public/register_customer.html')


@app.route('/register/agent', methods=['GET', 'POST'])
def register_agent():
    """Booking agent registration"""
    if request.method == 'POST':
        email = sanitize_string(request.form.get('email'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        errors = []
        if not email or not validate_email(email):
            errors.append('Valid email is required.')
        
        is_valid, pwd_error = validate_password_strength(password)
        if not is_valid:
            errors.append(pwd_error)
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if email exists
        existing = execute_query(
            "SELECT email FROM booking_agent WHERE email = %s",
            (email,), fetch_one=True
        )
        if existing:
            errors.append('Email already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('public/register_agent.html')
        
        hashed_pw = hash_password(password)
        try:
            execute_query(
                "INSERT INTO booking_agent (email, password) VALUES (%s, %s)",
                (email, hashed_pw), commit=True
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('public/register_agent.html')


@app.route('/register/staff', methods=['GET', 'POST'])
def register_staff():
    """Airline staff registration"""
    # Get list of airlines for dropdown
    airlines = execute_query("SELECT airline_name FROM airline")
    
    if request.method == 'POST':
        username = sanitize_string(request.form.get('username'))
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = sanitize_string(request.form.get('first_name'))
        last_name = sanitize_string(request.form.get('last_name'))
        date_of_birth = sanitize_string(request.form.get('date_of_birth'))
        airline_name = sanitize_string(request.form.get('airline_name'))
        
        errors = []
        if not username:
            errors.append('Username is required.')
        if not first_name or not last_name:
            errors.append('First and last name are required.')
        if not airline_name:
            errors.append('Airline selection is required.')
        
        is_valid, pwd_error = validate_password_strength(password)
        if not is_valid:
            errors.append(pwd_error)
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if date_of_birth and not validate_date(date_of_birth):
            errors.append('Invalid date of birth format.')
        
        # Check if username exists
        existing = execute_query(
            "SELECT username FROM airline_staff WHERE username = %s",
            (username,), fetch_one=True
        )
        if existing:
            errors.append('Username already taken.')
        
        # Verify airline exists
        airline_exists = execute_query(
            "SELECT airline_name FROM airline WHERE airline_name = %s",
            (airline_name,), fetch_one=True
        )
        if not airline_exists:
            errors.append('Invalid airline selected.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('public/register_staff.html', airlines=airlines)
        
        hashed_pw = hash_password(password)
        try:
            execute_query(
                """INSERT INTO airline_staff 
                   (username, password, first_name, last_name, date_of_birth, airline_name)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (username, hashed_pw, first_name, last_name, date_of_birth, airline_name),
                commit=True
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('public/register_staff.html', airlines=airlines)


@app.route('/search', methods=['GET', 'POST'])
@limiter.limit("30 per minute")  # Rate limit for search
def search_flights():
    """Public flight search"""
    flights = []

    if request.method == 'POST':
        source = sanitize_string(request.form.get('source'))
        destination = sanitize_string(request.form.get('destination'))
        departure_date = sanitize_string(request.form.get('departure_date'))

        # Build query dynamically with prepared statements
        # Updated to match actual database schema: airline_id, city column, lowercase status
        query = """
            SELECT f.*,
                   al.airline_name,
                   a1.city as departure_city,
                   a1.airport_name as departure_airport_name,
                   a2.city as arrival_city,
                   a2.airport_name as arrival_airport_name
            FROM flight f
            JOIN airline al ON f.airline_id = al.airline_id
            JOIN airport a1 ON f.departure_airport = a1.airport_code
            JOIN airport a2 ON f.arrival_airport = a2.airport_code
            WHERE LOWER(f.status) = 'upcoming'
            AND f.departure_time > NOW()
        """
        params = []

        if source:
            query += " AND (f.departure_airport LIKE %s OR a1.city LIKE %s OR a1.airport_name LIKE %s)"
            params.extend([f'%{source}%', f'%{source}%', f'%{source}%'])

        if destination:
            query += " AND (f.arrival_airport LIKE %s OR a2.city LIKE %s OR a2.airport_name LIKE %s)"
            params.extend([f'%{destination}%', f'%{destination}%', f'%{destination}%'])

        if departure_date:
            if validate_date(departure_date):
                query += " AND DATE(f.departure_time) = %s"
                params.append(departure_date)
            else:
                flash('Invalid date format. Use YYYY-MM-DD.', 'error')
                return render_template('public/search_flights.html', flights=flights)

        query += " ORDER BY f.departure_time LIMIT 50"

        try:
            result = execute_query(query, tuple(params))
            # Ensure flights is always a list, even if execute_query returns None
            flights = result if result is not None else []

            # Log search activity
            search_params = f"source={source}, dest={destination}, date={departure_date}"
            app.logger.info(f'Flight search performed: {search_params}, results={len(flights)}')

        except Exception as e:
            app.logger.error(f'Flight search failed: {str(e)}')
            flash('An error occurred while searching for flights. Please try again.', 'error')
            flights = []

    return render_template('public/search_flights.html', flights=flights)


@app.route('/flight_status', methods=['GET', 'POST'])
def flight_status():
    """Check flight status"""
    flight = None
    
    if request.method == 'POST':
        airline = sanitize_string(request.form.get('airline'))
        flight_num = sanitize_string(request.form.get('flight_num'))
        departure_date = sanitize_string(request.form.get('departure_date'))
        
        if not airline or not flight_num:
            flash('Please provide airline and flight number.', 'error')
        else:
            query = """
                SELECT f.*,
                       al.airline_name,
                       a1.city as departure_city,
                       a1.airport_name as departure_airport_name,
                       a2.city as arrival_city,
                       a2.airport_name as arrival_airport_name
                FROM flight f
                JOIN airline al ON f.airline_id = al.airline_id
                JOIN airport a1 ON f.departure_airport = a1.airport_code
                JOIN airport a2 ON f.arrival_airport = a2.airport_code
                WHERE al.airline_name = %s AND f.flight_num = %s
            """
            params = [airline, flight_num]
            
            if departure_date and validate_date(departure_date):
                query += " AND DATE(f.departure_time) = %s"
                params.append(departure_date)
            
            query += " ORDER BY f.departure_time DESC LIMIT 1"
            
            flight = execute_query(query, tuple(params), fetch_one=True)
            
            if not flight:
                flash('Flight not found.', 'error')
    
    # Get list of airlines for dropdown
    airlines = execute_query("SELECT airline_name FROM airline")
    
    return render_template('public/flight_status.html', flight=flight, airlines=airlines)


# ============================================================================
# CUSTOMER ROUTES
# ============================================================================

@app.route('/customer')
@app.route('/customer/home')
@login_required
@customer_required
def customer_home():
    """Customer home - show upcoming flights"""
    flights = execute_query("""
        SELECT f.*, t.ticket_id,
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        WHERE p.customer_email = %s 
        AND f.departure_time > NOW()
        ORDER BY f.departure_time
    """, (session['user'],))
    
    return render_template('customer/home.html', flights=flights)


@app.route('/customer/my_flights', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_my_flights():
    """View all customer flights with filters"""
    # Get filter parameters
    start_date = sanitize_string(request.form.get('start_date')) if request.method == 'POST' else None
    end_date = sanitize_string(request.form.get('end_date')) if request.method == 'POST' else None
    source = sanitize_string(request.form.get('source')) if request.method == 'POST' else None
    destination = sanitize_string(request.form.get('destination')) if request.method == 'POST' else None
    
    query = """
        SELECT f.*, t.ticket_id,
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city,
               p.purchase_date
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        WHERE p.customer_email = %s
    """
    params = [session['user']]
    
    if start_date and validate_date(start_date):
        query += " AND DATE(f.departure_time) >= %s"
        params.append(start_date)
    
    if end_date and validate_date(end_date):
        query += " AND DATE(f.departure_time) <= %s"
        params.append(end_date)
    
    if source:
        query += " AND (f.departure_airport LIKE %s OR a1.airport_city LIKE %s)"
        params.extend([f'%{source}%', f'%{source}%'])
    
    if destination:
        query += " AND (f.arrival_airport LIKE %s OR a2.airport_city LIKE %s)"
        params.extend([f'%{destination}%', f'%{destination}%'])
    
    query += " ORDER BY f.departure_time DESC"
    
    flights = execute_query(query, tuple(params))
    
    return render_template('customer/my_flights.html', flights=flights)


@app.route('/customer/purchase', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_purchase():
    """Search and purchase flights"""
    flights = []
    
    if request.method == 'POST' and 'search' in request.form:
        # Search for flights
        source = sanitize_string(request.form.get('source'))
        destination = sanitize_string(request.form.get('destination'))
        departure_date = sanitize_string(request.form.get('departure_date'))
        
        query = """
            SELECT f.*, 
                   a1.airport_city as departure_city,
                   a2.airport_city as arrival_city,
                   ap.seats as total_seats,
                   (SELECT COUNT(*) FROM ticket t2 
                    WHERE t2.airline_name = f.airline_name 
                    AND t2.flight_num = f.flight_num) as sold_tickets
            FROM flight f
            JOIN airport a1 ON f.departure_airport = a1.airport_name
            JOIN airport a2 ON f.arrival_airport = a2.airport_name
            JOIN airplane ap ON f.airplane_id = ap.airplane_id AND f.airline_name = ap.airline_name
            WHERE f.status = 'Upcoming'
            AND f.departure_time > NOW()
        """
        params = []
        
        if source:
            query += " AND (f.departure_airport LIKE %s OR a1.airport_city LIKE %s)"
            params.extend([f'%{source}%', f'%{source}%'])
        
        if destination:
            query += " AND (f.arrival_airport LIKE %s OR a2.airport_city LIKE %s)"
            params.extend([f'%{destination}%', f'%{destination}%'])
        
        if departure_date and validate_date(departure_date):
            query += " AND DATE(f.departure_time) = %s"
            params.append(departure_date)
        
        query += " ORDER BY f.departure_time LIMIT 50"
        
        flights = execute_query(query, tuple(params))
        
        # Calculate available seats for each flight
        for flight in flights:
            flight['available_seats'] = flight['total_seats'] - flight['sold_tickets']
    
    return render_template('customer/purchase.html', flights=flights)


@app.route('/customer/purchase/<airline>/<flight_num>/<departure_time>', methods=['POST'])
@login_required
@customer_required
@limiter.limit("10 per minute")  # Prevent rapid ticket purchases
def customer_purchase_ticket(airline, flight_num, departure_time):
    """Process ticket purchase"""
    airline = sanitize_string(airline)
    flight_num = sanitize_string(flight_num)
    departure_time = sanitize_string(departure_time)

    # Verify flight exists and has capacity
    flight = execute_query("""
        SELECT f.*, ap.seats as total_seats,
               (SELECT COUNT(*) FROM ticket t2
                WHERE t2.airline_name = f.airline_name
                AND t2.flight_num = f.flight_num) as sold_tickets
        FROM flight f
        JOIN airplane ap ON f.airplane_id = ap.airplane_id AND f.airline_name = ap.airline_name
        WHERE f.airline_name = %s AND f.flight_num = %s AND f.departure_time = %s
        AND f.status = 'Upcoming'
    """, (airline, flight_num, departure_time), fetch_one=True)

    if not flight:
        app.logger.warning(f'Purchase attempt for non-existent flight: {airline} {flight_num}')
        flash('Flight not found or no longer available.', 'error')
        return redirect(url_for('customer_purchase'))

    if flight['sold_tickets'] >= flight['total_seats']:
        app.logger.info(f'Purchase attempt for full flight: {airline} {flight_num}')
        flash('Sorry, this flight is fully booked.', 'error')
        return redirect(url_for('customer_purchase'))

    # Create ticket and purchase
    try:
        # Insert ticket
        ticket_id = execute_query(
            "INSERT INTO ticket (airline_name, flight_num) VALUES (%s, %s)",
            (airline, flight_num), commit=True
        )

        # Insert purchase record
        execute_query(
            """INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
               VALUES (%s, %s, NULL, NOW())""",
            (ticket_id, session['user']), commit=True
        )

        # Log successful purchase
        purchase_details = f'Ticket {ticket_id} for flight {airline} {flight_num} on {departure_time}'
        log_user_action('ticket_purchase', session['user'], purchase_details)
        app.logger.info(f'Ticket purchased: {purchase_details} by {session["user"]}')

        flash('Ticket purchased successfully!', 'success')

    except Exception as e:
        app.logger.error(f'Purchase failed for {session["user"]}: {str(e)}')
        flash('Purchase failed. Please try again.', 'error')

    return redirect(url_for('customer_home'))


@app.route('/customer/spending', methods=['GET', 'POST'])
@login_required
@customer_required
def customer_spending():
    """View spending analytics"""
    # Default: last 12 months total
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    if request.method == 'POST':
        custom_start = sanitize_string(request.form.get('start_date'))
        custom_end = sanitize_string(request.form.get('end_date'))
        
        if custom_start and validate_date(custom_start):
            start_date = datetime.strptime(custom_start, '%Y-%m-%d')
        if custom_end and validate_date(custom_end):
            end_date = datetime.strptime(custom_end, '%Y-%m-%d')
    
    # Total spending in period
    total_spending = execute_query("""
        SELECT COALESCE(SUM(f.price), 0) as total
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s
        AND p.purchase_date BETWEEN %s AND %s
    """, (session['user'], start_date, end_date), fetch_one=True)
    
    # Monthly breakdown for chart
    monthly_spending = execute_query("""
        SELECT DATE_FORMAT(p.purchase_date, '%%Y-%%m') as month,
               COALESCE(SUM(f.price), 0) as total
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.customer_email = %s
        AND p.purchase_date BETWEEN %s AND %s
        GROUP BY DATE_FORMAT(p.purchase_date, '%%Y-%%m')
        ORDER BY month
    """, (session['user'], start_date, end_date))
    
    return render_template('customer/spending.html',
                         total_spending=total_spending['total'],
                         monthly_spending=monthly_spending,
                         start_date=start_date.strftime('%Y-%m-%d'),
                         end_date=end_date.strftime('%Y-%m-%d'))


# ============================================================================
# BOOKING AGENT ROUTES
# ============================================================================

@app.route('/agent')
@app.route('/agent/home')
@login_required
@agent_required
def agent_home():
    """Booking agent home - show recent bookings"""
    bookings = execute_query("""
        SELECT f.*, t.ticket_id, p.customer_email, p.purchase_date,
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        WHERE p.booking_agent_id = %s
        ORDER BY p.purchase_date DESC
        LIMIT 20
    """, (session['agent_id'],))
    
    return render_template('agent/home.html', bookings=bookings)


@app.route('/agent/my_bookings', methods=['GET', 'POST'])
@login_required
@agent_required
def agent_my_bookings():
    """View all bookings with filters"""
    start_date = sanitize_string(request.form.get('start_date')) if request.method == 'POST' else None
    end_date = sanitize_string(request.form.get('end_date')) if request.method == 'POST' else None
    source = sanitize_string(request.form.get('source')) if request.method == 'POST' else None
    destination = sanitize_string(request.form.get('destination')) if request.method == 'POST' else None
    
    query = """
        SELECT f.*, t.ticket_id, p.customer_email, p.purchase_date,
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city
        FROM flight f
        JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
        JOIN purchases p ON t.ticket_id = p.ticket_id
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        WHERE p.booking_agent_id = %s
    """
    params = [session['agent_id']]
    
    if start_date and validate_date(start_date):
        query += " AND DATE(f.departure_time) >= %s"
        params.append(start_date)
    
    if end_date and validate_date(end_date):
        query += " AND DATE(f.departure_time) <= %s"
        params.append(end_date)
    
    if source:
        query += " AND (f.departure_airport LIKE %s OR a1.airport_city LIKE %s)"
        params.extend([f'%{source}%', f'%{source}%'])
    
    if destination:
        query += " AND (f.arrival_airport LIKE %s OR a2.airport_city LIKE %s)"
        params.extend([f'%{destination}%', f'%{destination}%'])
    
    query += " ORDER BY p.purchase_date DESC"
    
    bookings = execute_query(query, tuple(params))
    
    return render_template('agent/my_bookings.html', bookings=bookings)


@app.route('/agent/purchase', methods=['GET', 'POST'])
@login_required
@agent_required
def agent_purchase():
    """Search and purchase flights for customers"""
    flights = []
    
    # Get airlines this agent works for
    authorized_airlines = execute_query("""
        SELECT airline_name FROM booking_agent_work_for WHERE email = %s
    """, (session['user'],))
    airline_names = [a['airline_name'] for a in authorized_airlines]
    
    if request.method == 'POST' and 'search' in request.form:
        source = sanitize_string(request.form.get('source'))
        destination = sanitize_string(request.form.get('destination'))
        departure_date = sanitize_string(request.form.get('departure_date'))
        
        if not airline_names:
            flash('You are not authorized to book for any airlines.', 'error')
        else:
            # Create placeholders for airline names
            placeholders = ','.join(['%s'] * len(airline_names))
            
            query = f"""
                SELECT f.*, 
                       a1.airport_city as departure_city,
                       a2.airport_city as arrival_city,
                       ap.seats as total_seats,
                       (SELECT COUNT(*) FROM ticket t2 
                        WHERE t2.airline_name = f.airline_name 
                        AND t2.flight_num = f.flight_num) as sold_tickets
                FROM flight f
                JOIN airport a1 ON f.departure_airport = a1.airport_name
                JOIN airport a2 ON f.arrival_airport = a2.airport_name
                JOIN airplane ap ON f.airplane_id = ap.airplane_id AND f.airline_name = ap.airline_name
                WHERE f.status = 'Upcoming'
                AND f.departure_time > NOW()
                AND f.airline_name IN ({placeholders})
            """
            params = list(airline_names)
            
            if source:
                query += " AND (f.departure_airport LIKE %s OR a1.airport_city LIKE %s)"
                params.extend([f'%{source}%', f'%{source}%'])
            
            if destination:
                query += " AND (f.arrival_airport LIKE %s OR a2.airport_city LIKE %s)"
                params.extend([f'%{destination}%', f'%{destination}%'])
            
            if departure_date and validate_date(departure_date):
                query += " AND DATE(f.departure_time) = %s"
                params.append(departure_date)
            
            query += " ORDER BY f.departure_time LIMIT 50"
            
            flights = execute_query(query, tuple(params))
            
            for flight in flights:
                flight['available_seats'] = flight['total_seats'] - flight['sold_tickets']
    
    return render_template('agent/purchase.html', flights=flights, airlines=airline_names)


@app.route('/agent/purchase/<airline>/<flight_num>/<departure_time>', methods=['POST'])
@login_required
@agent_required
def agent_purchase_ticket(airline, flight_num, departure_time):
    """Process ticket purchase for customer"""
    airline = sanitize_string(airline)
    flight_num = sanitize_string(flight_num)
    departure_time = sanitize_string(departure_time)
    customer_email = sanitize_string(request.form.get('customer_email'))
    
    # Validate customer email
    if not customer_email or not validate_email(customer_email):
        flash('Valid customer email is required.', 'error')
        return redirect(url_for('agent_purchase'))
    
    # Verify customer exists
    customer = execute_query(
        "SELECT email FROM customer WHERE email = %s",
        (customer_email,), fetch_one=True
    )
    if not customer:
        flash('Customer not found.', 'error')
        return redirect(url_for('agent_purchase'))
    
    # Verify agent is authorized for this airline
    authorized = execute_query(
        "SELECT * FROM booking_agent_work_for WHERE email = %s AND airline_name = %s",
        (session['user'], airline), fetch_one=True
    )
    if not authorized:
        flash('You are not authorized to book for this airline.', 'error')
        return redirect(url_for('agent_purchase'))
    
    # Verify flight exists and has capacity
    flight = execute_query("""
        SELECT f.*, ap.seats as total_seats,
               (SELECT COUNT(*) FROM ticket t2 
                WHERE t2.airline_name = f.airline_name 
                AND t2.flight_num = f.flight_num) as sold_tickets
        FROM flight f
        JOIN airplane ap ON f.airplane_id = ap.airplane_id AND f.airline_name = ap.airline_name
        WHERE f.airline_name = %s AND f.flight_num = %s AND f.departure_time = %s
        AND f.status = 'Upcoming'
    """, (airline, flight_num, departure_time), fetch_one=True)
    
    if not flight:
        flash('Flight not found or no longer available.', 'error')
        return redirect(url_for('agent_purchase'))
    
    if flight['sold_tickets'] >= flight['total_seats']:
        flash('Sorry, this flight is fully booked.', 'error')
        return redirect(url_for('agent_purchase'))
    
    # Create ticket and purchase
    try:
        ticket_id = execute_query(
            "INSERT INTO ticket (airline_name, flight_num) VALUES (%s, %s)",
            (airline, flight_num), commit=True
        )
        
        execute_query(
            """INSERT INTO purchases (ticket_id, customer_email, booking_agent_id, purchase_date)
               VALUES (%s, %s, %s, NOW())""",
            (ticket_id, customer_email, session['agent_id']), commit=True
        )
        
        flash(f'Ticket purchased for {customer_email}!', 'success')
    except Exception as e:
        flash('Purchase failed. Please try again.', 'error')
    
    return redirect(url_for('agent_home'))


@app.route('/agent/analytics')
@login_required
@agent_required
def agent_analytics():
    """View commission and performance analytics"""
    # Commission totals for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    commission_stats = execute_query("""
        SELECT 
            COUNT(*) as ticket_count,
            COALESCE(SUM(f.price * 0.10), 0) as total_commission,
            COALESCE(AVG(f.price * 0.10), 0) as avg_commission
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.booking_agent_id = %s
        AND p.purchase_date >= %s
    """, (session['agent_id'], thirty_days_ago), fetch_one=True)
    
    # Top 5 customers by tickets (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    top_customers_tickets = execute_query("""
        SELECT p.customer_email, COUNT(*) as ticket_count
        FROM purchases p
        WHERE p.booking_agent_id = %s
        AND p.purchase_date >= %s
        GROUP BY p.customer_email
        ORDER BY ticket_count DESC
        LIMIT 5
    """, (session['agent_id'], six_months_ago))
    
    # Top 5 customers by commission (last year)
    one_year_ago = datetime.now() - timedelta(days=365)
    top_customers_commission = execute_query("""
        SELECT p.customer_email, SUM(f.price * 0.10) as commission
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE p.booking_agent_id = %s
        AND p.purchase_date >= %s
        GROUP BY p.customer_email
        ORDER BY commission DESC
        LIMIT 5
    """, (session['agent_id'], one_year_ago))
    
    return render_template('agent/analytics.html',
                         commission_stats=commission_stats,
                         top_customers_tickets=top_customers_tickets,
                         top_customers_commission=top_customers_commission)


# ============================================================================
# AIRLINE STAFF ROUTES
# ============================================================================

@app.route('/staff')
@app.route('/staff/home')
@login_required
@staff_required
def staff_home():
    """Staff home - show flights in next 30 days"""
    flights = execute_query("""
        SELECT f.*, 
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city,
               ap.seats as total_seats,
               (SELECT COUNT(*) FROM ticket t2 
                WHERE t2.airline_name = f.airline_name 
                AND t2.flight_num = f.flight_num) as sold_tickets
        FROM flight f
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        JOIN airplane ap ON f.airplane_id = ap.airplane_id AND f.airline_name = ap.airline_name
        WHERE f.airline_name = %s
        AND f.departure_time BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
        ORDER BY f.departure_time
    """, (session['airline'],))
    
    return render_template('staff/home.html', flights=flights)


@app.route('/staff/flights', methods=['GET', 'POST'])
@login_required
@staff_required
def staff_flights():
    """View all flights with filters"""
    start_date = sanitize_string(request.form.get('start_date')) if request.method == 'POST' else None
    end_date = sanitize_string(request.form.get('end_date')) if request.method == 'POST' else None
    source = sanitize_string(request.form.get('source')) if request.method == 'POST' else None
    destination = sanitize_string(request.form.get('destination')) if request.method == 'POST' else None
    
    query = """
        SELECT f.*, 
               a1.airport_city as departure_city,
               a2.airport_city as arrival_city
        FROM flight f
        JOIN airport a1 ON f.departure_airport = a1.airport_name
        JOIN airport a2 ON f.arrival_airport = a2.airport_name
        WHERE f.airline_name = %s
    """
    params = [session['airline']]
    
    if start_date and validate_date(start_date):
        query += " AND DATE(f.departure_time) >= %s"
        params.append(start_date)
    
    if end_date and validate_date(end_date):
        query += " AND DATE(f.departure_time) <= %s"
        params.append(end_date)
    
    if source:
        query += " AND (f.departure_airport LIKE %s OR a1.airport_city LIKE %s)"
        params.extend([f'%{source}%', f'%{source}%'])
    
    if destination:
        query += " AND (f.arrival_airport LIKE %s OR a2.airport_city LIKE %s)"
        params.extend([f'%{destination}%', f'%{destination}%'])
    
    query += " ORDER BY f.departure_time DESC"
    
    flights = execute_query(query, tuple(params))
    
    return render_template('staff/flights.html', flights=flights, statuses=ALLOWED_FLIGHT_STATUSES)


@app.route('/staff/passengers/<flight_num>/<departure_time>')
@login_required
@staff_required
def staff_passengers(flight_num, departure_time):
    """View passengers on a flight"""
    flight_num = sanitize_string(flight_num)
    departure_time = sanitize_string(departure_time)
    
    # Verify flight belongs to staff's airline
    flight = execute_query(
        "SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND departure_time = %s",
        (session['airline'], flight_num, departure_time), fetch_one=True
    )
    
    if not flight:
        flash('Flight not found.', 'error')
        return redirect(url_for('staff_flights'))
    
    passengers = execute_query("""
        SELECT c.*, t.ticket_id, p.purchase_date, p.booking_agent_id
        FROM customer c
        JOIN purchases p ON c.email = p.customer_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s AND t.flight_num = %s
    """, (session['airline'], flight_num))
    
    return render_template('staff/passengers.html', flight=flight, passengers=passengers)


@app.route('/staff/customer_flights', methods=['GET', 'POST'])
@login_required
@staff_required
def staff_customer_flights():
    """View flights taken by a specific customer"""
    flights = []
    customer_email = None
    
    if request.method == 'POST':
        customer_email = sanitize_string(request.form.get('customer_email'))
        
        if customer_email and validate_email(customer_email):
            flights = execute_query("""
                SELECT f.*, t.ticket_id, p.purchase_date,
                       a1.airport_city as departure_city,
                       a2.airport_city as arrival_city
                FROM flight f
                JOIN ticket t ON f.airline_name = t.airline_name AND f.flight_num = t.flight_num
                JOIN purchases p ON t.ticket_id = p.ticket_id
                JOIN airport a1 ON f.departure_airport = a1.airport_name
                JOIN airport a2 ON f.arrival_airport = a2.airport_name
                WHERE p.customer_email = %s
                AND f.airline_name = %s
                ORDER BY f.departure_time DESC
            """, (customer_email, session['airline']))
        else:
            flash('Please enter a valid email.', 'error')
    
    return render_template('staff/customer_flights.html', flights=flights, customer_email=customer_email)


@app.route('/staff/update_status', methods=['POST'])
@login_required
@staff_required
@operator_required
def staff_update_status():
    """Update flight status (Operator only)"""
    flight_num = sanitize_string(request.form.get('flight_num'))
    departure_time = sanitize_string(request.form.get('departure_time'))
    new_status = sanitize_string(request.form.get('status'))
    
    # Validate status
    if not validate_flight_status(new_status):
        flash('Invalid status.', 'error')
        return redirect(url_for('staff_flights'))
    
    # Update status
    result = execute_query(
        """UPDATE flight SET status = %s 
           WHERE airline_name = %s AND flight_num = %s AND departure_time = %s""",
        (new_status, session['airline'], flight_num, departure_time), commit=True
    )
    
    flash('Flight status updated.', 'success')
    return redirect(url_for('staff_flights'))


@app.route('/staff/add_airplane', methods=['GET', 'POST'])
@login_required
@staff_required
@admin_required
def staff_add_airplane():
    """Add new airplane (Admin only)"""
    if request.method == 'POST':
        airplane_id = sanitize_string(request.form.get('airplane_id'))
        seats = sanitize_int(request.form.get('seats'), min_val=1)
        
        if not airplane_id:
            flash('Airplane ID is required.', 'error')
        elif not seats:
            flash('Valid number of seats is required.', 'error')
        else:
            # Check if airplane already exists
            existing = execute_query(
                "SELECT * FROM airplane WHERE airline_name = %s AND airplane_id = %s",
                (session['airline'], airplane_id), fetch_one=True
            )
            if existing:
                flash('Airplane ID already exists.', 'error')
            else:
                try:
                    execute_query(
                        "INSERT INTO airplane (airline_name, airplane_id, seats) VALUES (%s, %s, %s)",
                        (session['airline'], airplane_id, seats), commit=True
                    )
                    flash('Airplane added successfully!', 'success')
                    return redirect(url_for('staff_home'))
                except Exception as e:
                    flash('Failed to add airplane.', 'error')
    
    return render_template('staff/add_airplane.html')


@app.route('/staff/add_airport', methods=['GET', 'POST'])
@login_required
@staff_required
@admin_required
def staff_add_airport():
    """Add new airport (Admin only)"""
    if request.method == 'POST':
        airport_name = sanitize_string(request.form.get('airport_name'))
        airport_city = sanitize_string(request.form.get('airport_city'))
        
        if not airport_name or not airport_city:
            flash('Airport name and city are required.', 'error')
        else:
            existing = execute_query(
                "SELECT * FROM airport WHERE airport_name = %s",
                (airport_name,), fetch_one=True
            )
            if existing:
                flash('Airport already exists.', 'error')
            else:
                try:
                    execute_query(
                        "INSERT INTO airport (airport_name, airport_city) VALUES (%s, %s)",
                        (airport_name, airport_city), commit=True
                    )
                    flash('Airport added successfully!', 'success')
                    return redirect(url_for('staff_home'))
                except Exception as e:
                    flash('Failed to add airport.', 'error')
    
    return render_template('staff/add_airport.html')


@app.route('/staff/add_flight', methods=['GET', 'POST'])
@login_required
@staff_required
@admin_required
def staff_add_flight():
    """Add new flight (Admin only)"""
    # Get airplanes and airports for dropdowns
    airplanes = execute_query(
        "SELECT * FROM airplane WHERE airline_name = %s",
        (session['airline'],)
    )
    airports = execute_query("SELECT * FROM airport")
    
    if request.method == 'POST':
        flight_num = sanitize_string(request.form.get('flight_num'))
        departure_airport = sanitize_string(request.form.get('departure_airport'))
        departure_time = sanitize_string(request.form.get('departure_time'))
        arrival_airport = sanitize_string(request.form.get('arrival_airport'))
        arrival_time = sanitize_string(request.form.get('arrival_time'))
        price = sanitize_float(request.form.get('price'), min_val=0)
        airplane_id = sanitize_string(request.form.get('airplane_id'))
        
        errors = []
        if not flight_num:
            errors.append('Flight number is required.')
        if not departure_airport or not arrival_airport:
            errors.append('Departure and arrival airports are required.')
        if departure_airport == arrival_airport:
            errors.append('Departure and arrival airports must be different.')
        if not departure_time or not validate_datetime(departure_time):
            errors.append('Valid departure time is required.')
        if not arrival_time or not validate_datetime(arrival_time):
            errors.append('Valid arrival time is required.')
        if price is None:
            errors.append('Valid price is required.')
        if not airplane_id:
            errors.append('Airplane selection is required.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            try:
                execute_query(
                    """INSERT INTO flight 
                       (airline_name, flight_num, departure_airport, departure_time, 
                        arrival_airport, arrival_time, price, status, airplane_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 'Upcoming', %s)""",
                    (session['airline'], flight_num, departure_airport, departure_time,
                     arrival_airport, arrival_time, price, airplane_id), commit=True
                )
                flash('Flight added successfully!', 'success')
                return redirect(url_for('staff_home'))
            except Exception as e:
                flash('Failed to add flight. It may already exist.', 'error')
    
    return render_template('staff/add_flight.html', airplanes=airplanes, airports=airports)


@app.route('/staff/add_agent', methods=['GET', 'POST'])
@login_required
@staff_required
@admin_required
def staff_add_agent():
    """Associate booking agent with airline (Admin only)"""
    if request.method == 'POST':
        agent_email = sanitize_string(request.form.get('agent_email'))
        
        if not agent_email or not validate_email(agent_email):
            flash('Valid agent email is required.', 'error')
        else:
            # Verify agent exists
            agent = execute_query(
                "SELECT * FROM booking_agent WHERE email = %s",
                (agent_email,), fetch_one=True
            )
            if not agent:
                flash('Booking agent not found.', 'error')
            else:
                # Check if already associated
                existing = execute_query(
                    "SELECT * FROM booking_agent_work_for WHERE email = %s AND airline_name = %s",
                    (agent_email, session['airline']), fetch_one=True
                )
                if existing:
                    flash('Agent is already associated with your airline.', 'error')
                else:
                    try:
                        execute_query(
                            "INSERT INTO booking_agent_work_for (email, airline_name) VALUES (%s, %s)",
                            (agent_email, session['airline']), commit=True
                        )
                        flash('Booking agent associated successfully!', 'success')
                    except Exception as e:
                        flash('Failed to associate agent.', 'error')
    
    return render_template('staff/add_agent.html')


@app.route('/staff/analytics')
@login_required
@staff_required
def staff_analytics():
    """View analytics dashboard"""
    # Top booking agents by tickets this month
    one_month_ago = datetime.now() - timedelta(days=30)
    top_agents_month = execute_query("""
        SELECT ba.email, COUNT(*) as ticket_count
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY ba.email
        ORDER BY ticket_count DESC
        LIMIT 5
    """, (session['airline'], one_month_ago))
    
    # Top booking agents by tickets this year
    one_year_ago = datetime.now() - timedelta(days=365)
    top_agents_year = execute_query("""
        SELECT ba.email, COUNT(*) as ticket_count
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY ba.email
        ORDER BY ticket_count DESC
        LIMIT 5
    """, (session['airline'], one_year_ago))
    
    # Top booking agents by commission this year
    top_agents_commission = execute_query("""
        SELECT ba.email, SUM(f.price * 0.10) as commission
        FROM booking_agent ba
        JOIN purchases p ON ba.booking_agent_id = p.booking_agent_id
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY ba.email
        ORDER BY commission DESC
        LIMIT 5
    """, (session['airline'], one_year_ago))
    
    # Most frequent customer last year
    frequent_customer = execute_query("""
        SELECT p.customer_email, COUNT(*) as flight_count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY p.customer_email
        ORDER BY flight_count DESC
        LIMIT 1
    """, (session['airline'], one_year_ago), fetch_one=True)
    
    # Tickets sold per month (last 12 months)
    tickets_monthly = execute_query("""
        SELECT DATE_FORMAT(p.purchase_date, '%%Y-%%m') as month, COUNT(*) as count
        FROM purchases p
        JOIN ticket t ON p.ticket_id = t.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY DATE_FORMAT(p.purchase_date, '%%Y-%%m')
        ORDER BY month
    """, (session['airline'], one_year_ago))
    
    # Flight delay statistics
    delay_stats = execute_query("""
        SELECT 
            SUM(CASE WHEN status = 'Delayed' THEN 1 ELSE 0 END) as delayed,
            SUM(CASE WHEN status != 'Delayed' THEN 1 ELSE 0 END) as on_time,
            COUNT(*) as total
        FROM flight
        WHERE airline_name = %s
        AND departure_time < NOW()
    """, (session['airline'],), fetch_one=True)
    
    # Top destinations (last 3 months)
    three_months_ago = datetime.now() - timedelta(days=90)
    top_destinations_3m = execute_query("""
        SELECT f.arrival_airport, a.airport_city, COUNT(*) as count
        FROM ticket t
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        JOIN airport a ON f.arrival_airport = a.airport_name
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY f.arrival_airport, a.airport_city
        ORDER BY count DESC
        LIMIT 5
    """, (session['airline'], three_months_ago))
    
    # Top destinations (last year)
    top_destinations_year = execute_query("""
        SELECT f.arrival_airport, a.airport_city, COUNT(*) as count
        FROM ticket t
        JOIN flight f ON t.airline_name = f.airline_name AND t.flight_num = f.flight_num
        JOIN airport a ON f.arrival_airport = a.airport_name
        JOIN purchases p ON t.ticket_id = p.ticket_id
        WHERE t.airline_name = %s
        AND p.purchase_date >= %s
        GROUP BY f.arrival_airport, a.airport_city
        ORDER BY count DESC
        LIMIT 5
    """, (session['airline'], one_year_ago))
    
    return render_template('staff/analytics.html',
                         top_agents_month=top_agents_month,
                         top_agents_year=top_agents_year,
                         top_agents_commission=top_agents_commission,
                         frequent_customer=frequent_customer,
                         tickets_monthly=tickets_monthly,
                         delay_stats=delay_stats,
                         top_destinations_3m=top_destinations_3m,
                         top_destinations_year=top_destinations_year)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def redirect_to_home():
    """Redirect user to their appropriate home page"""
    user_type = session.get('user_type')
    if user_type == 'customer':
        return redirect(url_for('customer_home'))
    elif user_type == 'agent':
        return redirect(url_for('agent_home'))
    elif user_type == 'staff':
        return redirect(url_for('staff_home'))
    return redirect(url_for('index'))


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    return render_template('public/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('public/500.html'), 500


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
