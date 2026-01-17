"""
DevLog Flask Backend
Georgian Junior Developer Community Platform

This is the main file that starts the app.
All the actual code is in separate files:
- config.py = settings
- models.py = database models
- auth.py = login/permissions
- database.py = database setup
- routes.py = all the pages
- errors.py = error pages
"""

from flask import Flask
from models import db
from config import Config
from database import init_db
from routes import setup_routes
from errors import setup_error_handlers
from auth import get_current_user


# Create the Flask app
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Set up all routes
setup_routes(app)

# Set up error handlers
setup_error_handlers(app)

# Make current user available in templates
@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}


# Run the app
if __name__ == '__main__':
    # Initialize database and add sample data
    init_db(app)
    
    print("\n" + "="*50)
    print("🚀 DevLog Flask Backend Started")
    print("="*50)
    print("\n✅ Demo Users:")
    print("  Username: demo  | Password: password123")
    print("  Username: admin | Password: admin123")
    print("\n🌍 http://localhost:5000/")
    print("\n💾 Database: devlog.db")
    print("="*50 + "\n")
    
    app.run(debug=True)
