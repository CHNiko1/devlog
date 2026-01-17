"""
Database setup and sample data seeding
This file handles creating tables and adding demo data
"""

from models import db, User, Post, Comment, Like, Repost
from datetime import datetime, timedelta


def init_db(app):
    """
    Create all database tables and add sample data
    This runs only once when the app starts
    """
    with app.app_context():
        # Create all tables from models
        db.create_all()
        
        # Check if we already have data
        if User.query.first() is not None:
            print("✅ Database already has data. Skipping seed.")
            return
        
        print("🌱 Seeding database with sample data...")
        
        # Create demo users
        demo_user = User(
            username='demo',
            email='demo@devlog.ge',
            password='password123',
            role='user'
        )
        admin_user = User(
            username='admin',
            email='admin@devlog.ge',
            password='admin123',
            role='admin'
        )
        
        db.session.add(demo_user)
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"✅ Created users: {demo_user.username}, {admin_user.username}")
        
        # Create sample posts
        post1 = Post(
            title='Python - პროგრამირების ენას, ეს სახელი გველის გამო არ ჰქვია ',
            content="""სახელი მოდის Monty Python’s Flying Circus-იდან (ბრიტანული კომედიური შოუ).
            ამის გამოა, რომ Python-ის დოკუმენტაციაში ხშირად ნახავ იუმორს..""",
            author=demo_user,
            language='Python',
            level='beginner',
            is_published=True,
            created_at=datetime.now() - timedelta(days=10)
        )
        
        db.session.add(post1)
        db.session.commit()
        
        print(f"✅ Created {Post.query.count()} posts")
        
        # Create sample comments
        comment1 = Comment(
            content='ჰაჰაჰა! ეს პირველად გავიგე',
            author=admin_user,
            post=post1,
            created_at=datetime.now() - timedelta(days=2)
        )
        
        db.session.add(comment1)
        db.session.commit()
        
        print(f"✅ Created {Comment.query.count()} comments")
        print("✅ Database initialized successfully!\n")
