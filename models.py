"""
Database Models for DevLog
Uses SQLAlchemy to define database tables
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Follow association table for many-to-many relationship
follow_association = db.Table(
    'follow_association',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)


class User(db.Model):
    """User model - stores user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    profile_photo = db.Column(db.String(255), default='/static/img/default-avatar.png')  # Profile photo URL
    bio = db.Column(db.Text, default='')  # User bio/description
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='author', lazy=True, cascade='all, delete-orphan')
    reposts = db.relationship('Repost', backref='author', lazy=True, cascade='all, delete-orphan')
    
    # Follow relationships
    following = db.relationship(
        'User',
        secondary=follow_association,
        primaryjoin=follow_association.c.follower_id == id,
        secondaryjoin=follow_association.c.followed_id == id,
        backref='followers',
        lazy=True
    )
    
    # Flask-Login required properties
    is_authenticated = True
    is_active = True
    is_anonymous = False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """Post model - stores blog posts"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)  # Python, JavaScript, etc.
    level = db.Column(db.String(50), nullable=False)  # beginner, junior, intermediate, advanced
    photo = db.Column(db.String(255))  # Photo filename for posts
    is_published = db.Column(db.Boolean, default=False)  # Admin approval needed
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Foreign key
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    reposts = db.relationship('Repost', backref='post', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Post {self.title}>'


class Like(db.Model):
    """Like model - when users like a post"""
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Make sure each user can only like a post once
    __table_args__ = (db.UniqueConstraint('post_id', 'author_id', name='unique_post_like'),)
    
    def __repr__(self):
        return f'<Like by user {self.author_id} on post {self.post_id}>'


class Repost(db.Model):
    """Repost model - when users share a post"""
    __tablename__ = 'reposts'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Make sure each user can only repost a post once
    __table_args__ = (db.UniqueConstraint('post_id', 'author_id', name='unique_post_repost'),)
    
    def __repr__(self):
        return f'<Repost by user {self.author_id} on post {self.post_id}>'
class Comment(db.Model):
    """Comment model - stores comments on posts"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Foreign keys
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Comment by {self.author.username}>'
