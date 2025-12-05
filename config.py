"""
Database Configuration and Connection Handler
Air Ticket Reservation System
"""

import pymysql

# ========== DATABASE CONFIGURATION ==========
# Update these values for your XAMPP setup
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Default XAMPP has no password
    'database': 'airline_portal',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset': 'utf8mb4'
}

# Flask app configuration
SECRET_KEY = 'change-this-to-a-very-long-random-string-in-production'


def get_db_connection():
    """Create and return a new database connection"""
    return pymysql.connect(**DB_CONFIG)


def execute_query(query, params=None, fetch_one=False, commit=False):
    """
    Execute a SQL query safely using prepared statements.
    
    Args:
        query: SQL query string with %s placeholders
        params: Tuple of parameters to substitute (prevents SQL injection)
        fetch_one: If True, return single row; otherwise return all rows
        commit: If True, commit the transaction (for INSERT/UPDATE/DELETE)
    
    Returns:
        Query results (dict or list of dicts) or lastrowid for inserts
    
    SECURITY: Always use params for user input - NEVER concatenate strings!
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return cursor.lastrowid
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    except pymysql.Error as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def execute_many(query, params_list, commit=True):
    """
    Execute a SQL query multiple times with different parameters.
    Useful for batch inserts.
    
    Args:
        query: SQL query string with %s placeholders
        params_list: List of tuples, each containing parameters for one execution
        commit: If True, commit after all executions
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(query, params_list)
        if commit:
            conn.commit()
        return cursor.rowcount
    except pymysql.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
