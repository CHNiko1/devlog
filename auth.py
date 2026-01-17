"""
Authentication helpers and decorators
Used to protect routes and check user permissions
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from models import User


def login_required(f):
    """
    This decorator checks if user is logged in
    If not, it sends them to login page
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('პირველ რიგში შედი.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    This decorator checks if user is admin
    If not, it shows an error message
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = get_current_user()
        if user.role != 'admin':
            flash('ამ გვერდზე წვდომა აქვთ მხოლოდ ადმინისტრატორებს.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Gets the user that is currently logged in
    Returns the User object or None if nobody is logged in
    """
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
