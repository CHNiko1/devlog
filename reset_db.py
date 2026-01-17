"""
Clean up the old database so we can recreate it with new models
Just run: python reset_db.py
"""

import os

db_path = 'devlog.db'

# Delete the old database
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted {db_path}")
else:
    print(f"❌ {db_path} not found")

print("\nNow run: python app.py")
print("This will create a fresh database with Like and Repost tables!")
