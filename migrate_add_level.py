"""
Migration script to add 'level' column to users table
Run this once to update existing database
"""

from app import app, db
from models import User

def migrate():
    """Add level column to existing users"""
    with app.app_context():
        try:
            # Try to add the column using raw SQL
            with db.engine.connect() as conn:
                # Check if column already exists
                result = conn.execute(db.text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]
                
                if 'level' not in columns:
                    print("Adding 'level' column to users table...")
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN level VARCHAR(50) DEFAULT 'beginner'"))
                    conn.commit()
                    print("✓ Column added successfully!")
                    
                    # Update existing users to have beginner level
                    conn.execute(db.text("UPDATE users SET level = 'beginner' WHERE level IS NULL"))
                    conn.commit()
                    print("✓ Existing users updated with default level!")
                else:
                    print("✓ Column 'level' already exists!")
                    
        except Exception as e:
            print(f"Error during migration: {e}")
            print("\nAlternative: You can reset the database by running:")
            print("python reset_db.py")

if __name__ == '__main__':
    migrate()
