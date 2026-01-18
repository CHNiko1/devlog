"""
DevLog Flask App
A social platform for Georgian developers
"""

from flask import Flask, session, redirect, url_for, flash, render_template
from models import db, User, Notification
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE_URL = f'sqlite:///{basedir}/devlog.db'
SECRET_KEY = 'my-secret-key'

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)


# Function to get logged in user
def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return user
    return None


# Function to check unread notifications
def get_unread_count():
    user = get_current_user()
    if user:
        # Get all unread notifications
        notifications = Notification.query.filter_by(user_id=user.id, is_read=False).all()
        count = len(notifications)
        return count
    return 0


# Make user available in templates
@app.context_processor
def inject_globals():
    user = get_current_user()
    if user:
        user.is_authenticated = True
    return {
        'current_user': user,
        'unread_notifications_count': get_unread_count()
    }


# Import all routes
from routes import setup_routes
setup_routes(app)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f'Server error: {error}')
    db.session.rollback()
    return render_template('500.html'), 500


# Initialize database on startup
def init_database(app):
    with app.app_context():
        db.create_all()

        # Check if users already exist
        if User.query.first() is not None:
            return

        # Create demo user
        demo = User(
            username='demo',
            email='demo@devlog.ge',
            password=generate_password_hash('password123'),
            role='user',
            level='beginner'
        )

        # Create admin user
        admin = User(
            username='admin',
            email='admin@devlog.ge',
            password=generate_password_hash('admin123'),
            role='admin',
            level='senior'
        )

        db.session.add(demo)
        db.session.add(admin)
        db.session.commit()


# Ensure database exists when the app loads (covers gunicorn)
init_database(app)


# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\nDevLog started")
    print("Demo user: demo / password123")
    print("Admin user: admin / admin123")
    print(f"\nhttp://localhost:{port}/\n")
    app.run(host='0.0.0.0', port=port, debug=True)
