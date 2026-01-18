# Render Deployment Guide

## Important: Database Setup

On Render, you **must** use PostgreSQL instead of SQLite because SQLite files are deleted on each deployment.

### Steps to Deploy on Render:

1. **Create a PostgreSQL Database** on Render:
   - Go to your Render dashboard
   - Click "New +" → "PostgreSQL"
   - Name it (e.g., "devlog-db")
   - Copy the **Internal Database URL**

2. **Configure Environment Variables** in your Web Service:
   - Go to your web service → Environment
   - Add these variables:
     - `DATABASE_URL` = (paste your Internal Database URL)
     - `SECRET_KEY` = (generate a random secret key)
     - `PYTHON_VERSION` = `3.11.0` (optional)

3. **Deploy Settings**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **First Deployment**:
   - The database will automatically initialize with:
     - Demo user: `demo` / `password123`
     - Admin user: `admin` / `admin123`
   - Check the logs to confirm users were created

### Troubleshooting Login Issues:

If you can't login on Render:
1. Check Render logs for error messages
2. Look for "Users already exist" or "Demo and Admin users created" messages
3. If users weren't created, you may need to manually trigger database initialization

### Local Development:
- Automatically uses SQLite (`devlog.db`)
- No DATABASE_URL environment variable needed
