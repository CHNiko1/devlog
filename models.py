"""
Database models
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Follow table
follow_table = db.Table(
    'follow_table',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    level = db.Column(db.String(50), default='beginner')
    gender = db.Column(db.String(20), default='other')
    profile_photo = db.Column(db.String(255), default='/static/images/avatar-default.png')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    posts = db.relationship('Post', backref='author')
    comments = db.relationship('Comment', backref='author')
    likes = db.relationship('Like', backref='author')
    reposts = db.relationship('Repost', backref='author')
    notifications = db.relationship('Notification', backref='recipient', foreign_keys='Notification.user_id')
    sent_notifications = db.relationship('Notification', backref='sender', foreign_keys='Notification.sender_id')
    messages_sent = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id')
    messages_received = db.relationship('Message', backref='receiver', foreign_keys='Message.receiver_id')
    
    following = db.relationship(
        'User',
        secondary=follow_table,
        primaryjoin=follow_table.c.follower_id == id,
        secondaryjoin=follow_table.c.followed_id == id,
        backref='followers'
    )
    
    def __repr__(self):
        return f'User({self.username})'


class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    language = db.Column(db.String(50))
    level = db.Column(db.String(50))
    photo = db.Column(db.String(255))
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    comments = db.relationship('Comment', backref='post', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', cascade='all, delete-orphan')
    reposts = db.relationship('Repost', backref='post', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='post', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'Post({self.title})'


class Like(db.Model):
    __tablename__ = 'likes'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Repost(db.Model):
    __tablename__ = 'reposts'
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'Comment({self.content[:20]})'


class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(50))
    message = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))


class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __repr__(self):
        return f'Message({self.content[:20]})'
