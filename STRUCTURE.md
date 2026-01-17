## DevLog - Refactored Structure 

Your app.py has been split into separate beginner-friendly files! 🎉

### File Structure

**Main Files:**
- `app.py` - The entry point (runs the app)
- `models.py` - Database models (User, Post, Comment)
- `config.py` - Settings and configuration
- `requirements.txt` - Python packages needed

**Logic Files:**
- `auth.py` - Login/authentication functions
- `routes.py` - All page routes (homepage, posts, login, etc)
- `database.py` - Database setup and sample data
- `errors.py` - Error page handlers

**Frontend:**
- `templates/` - HTML pages
- `static/` - CSS and JavaScript files

### How It Works

1. **app.py** - Starts everything:
   - Creates the Flask app
   - Loads configuration
   - Sets up routes
   - Sets up error handlers
   - Initializes database

2. **config.py** - All settings in one place:
   - Database location
   - Secret key
   - Other Flask settings

3. **auth.py** - Handles users:
   - `login_required` - Stops non-logged-in users
   - `admin_required` - Stops non-admin users
   - `get_current_user()` - Gets who is logged in

4. **database.py** - Sets up the database:
   - Creates tables
   - Adds demo data

5. **routes.py** - All the pages:
   - Home page
   - View posts
   - Create posts
   - Admin panel
   - Login/Register
   - Comments

6. **errors.py** - Error pages:
   - 404 error (page not found)
   - 500 error (server problem)

### How to Run

```bash
python app.py
```

Then go to: `http://localhost:5000/`

### Demo Users

- **Username:** demo  **Password:** password123
- **Username:** admin  **Password:** admin123

### Why This Structure?

✅ **Easy to understand** - Each file has one job  
✅ **Easy to find things** - Know where to look  
✅ **Easy to add features** - Add new routes in routes.py  
✅ **Beginner friendly** - Clear comments everywhere  

### To Add a New Route

1. Go to `routes.py`
2. Find the `setup_routes(app)` function
3. Add your new route inside it
4. Save and restart `app.py`

### To Add a New Model

1. Go to `models.py`
2. Create a new class (like User, Post, Comment)
3. It will automatically create a database table

### Important Notes

⚠️ The passwords are NOT hashed! In production, you must use `werkzeug.security` or similar to hash passwords.

⚠️ Change the `SECRET_KEY` in `config.py` before going live!
