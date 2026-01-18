"""
Fix existing users with hashed passwords
"""

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Update demo user
    demo = User.query.filter_by(username='demo').first()
    if demo:
        demo.password = generate_password_hash('password123')
        db.session.commit()
        print("✓ Demo user password updated")
    
    # Update admin user
    admin = User.query.filter_by(username='admin').first()
    if admin:
        admin.password = generate_password_hash('admin123')
        db.session.commit()
        print("✓ Admin user password updated")
    
    print("\nPasswords fixed! You can now login:")
    print("Demo: demo / password123")
    print("Admin: admin / admin123")
