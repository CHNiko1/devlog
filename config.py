"""
Configuration settings for DevLog app
"""

import os

# Get the folder where this file is located
basedir = os.path.abspath(os.path.dirname(__file__))

# Database path
DATABASE_PATH = f'sqlite:///{basedir}/devlog.db'

# Secret key for sessions (change this in production!)
SECRET_KEY = 'your-secret-key-change-in-production'

# These are the settings we give to Flask
class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_PATH
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = SECRET_KEY
