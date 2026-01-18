"""
All routes for DevLog app
"""

import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash

from models import db, User, Post, Comment, Like, Repost, Notification, Message


# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def setup_routes(app):
    """Setup all routes"""
    
    from app import get_current_user

    # Delete post
    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    def delete_post(post_id):
        """Delete a post"""
        user = get_current_user()
        
        # Check if user is logged in
        if user is None:
            flash('You need to be logged in', 'warning')
            return redirect(url_for('login'))
        
        try:
            post = Post.query.get(post_id)
            if post is None:
                return "Post not found", 404

            # Check if user is author or admin
            if post.author_id != user.id and user.role != 'admin':
                flash('You cannot delete this post', 'danger')
                return redirect(url_for('post_detail', post_id=post_id))

            db.session.delete(post)
            db.session.commit()
            flash('Post deleted', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('user_profile', username=user.username))
        except Exception as e:
            db.session.rollback()
            flash('Error deleting post', 'danger')
            return redirect(url_for('post_detail', post_id=post_id))

    # Home page
    @app.route('/')
    def index():
        """Home page"""
        posts = Post.query.filter_by(is_published=True)
        posts = posts.order_by(Post.created_at.desc())
        posts = posts.limit(6)
        posts = posts.all()
        return render_template('index.html', posts=posts)
    
    
    # All posts
    @app.route('/posts')
    def posts():
        """All posts page with search and filters"""
        try:
            q = request.args.get('q', '')
            language = request.args.get('language', '')
            level = request.args.get('level', '')
            
            # Get all posts that are published
            posts_list = Post.query.filter_by(is_published=True)
            
            # Filter by search using SQL LIKE
            if q:
                posts_list = posts_list.filter(
                    (Post.title.ilike(f'%{q}%')) | 
                    (Post.content.ilike(f'%{q}%'))
                )
            
            # Filter by language
            if language:
                posts_list = posts_list.filter_by(language=language)
            
            # Filter by level
            if level:
                posts_list = posts_list.filter_by(level=level)
            
            # Sort by newest first
            posts_list = posts_list.order_by(Post.created_at.desc()).all()
            
            # Save active filters
            active_filters = {
                'q': q,
                'language': language,
                'level': level
            }
            
            return render_template('posts.html', posts=posts_list, filters=active_filters)
        except Exception as e:
            flash('Error loading posts', 'danger')
            return redirect(url_for('index'))
    
    
    # Clear filters
    @app.route('/posts/clear-filters')
    def clear_filters():
        """Clear all filters and show all posts"""
        # Redirect back to posts page with no filters
        return redirect(url_for('posts'))
    
    # View single post
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        """View a single post with comments"""
        post = Post.query.get(post_id)
        if post is None:
            return "Post not found", 404
        return render_template('post_detail.html', post=post)
    
    
    # Create post
    @app.route('/create-post', methods=['GET', 'POST'])
    def create_post():
        """Create a new post (user must be logged in)"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            language = request.form.get('language', '')
            level = request.form.get('level', '')
            
            if not title or not content:
                flash('Title and content are required', 'danger')
                return render_template('create_post.html')
            
            try:
                # Handle photo upload
                photo_filename = None
                if 'photo' in request.files:
                    photo = request.files['photo']
                    if photo and photo.filename != '' and allowed_file(photo.filename):
                        # Check file size
                        photo.seek(0, os.SEEK_END)
                        file_length = photo.tell()
                        photo.seek(0)
                        if file_length > MAX_FILE_SIZE:
                            flash('Image too large (max 5MB)', 'danger')
                            return render_template('create_post.html')
                        
                        # Create posts directory if it doesn't exist
                        posts_dir = os.path.join('static', 'uploads', 'posts')
                        os.makedirs(posts_dir, exist_ok=True)
                        
                        # Save file with secure filename
                        filename = secure_filename(photo.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                        filename = timestamp + filename
                        photo.save(os.path.join(posts_dir, filename))
                        photo_filename = filename
                
                # Create new post
                new_post = Post(
                    title=title,
                    content=content,
                    author=get_current_user(),
                    language=language,
                    level=level,
                    photo=photo_filename,
                    is_published=False  # Admin needs to approve
                )
                
                db.session.add(new_post)
                db.session.commit()
                
                flash('პოსტი დაიპოსტა, ადმინდა დაადასტურა', 'success')
                return redirect(url_for('my_posts'))
            except Exception as e:
                db.session.rollback()
                flash('Error creating post', 'danger')
                return render_template('create_post.html')
        
        return render_template('create_post.html')
    
    
    # My posts
    @app.route('/my-posts')
    def my_posts():
        """Redirect to user's profile page"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return redirect(url_for('user_profile', username=user.username))
    
    
    # Add comment
    @app.route('/post/<int:post_id>/comment', methods=['POST'])
    def add_comment(post_id):
        """Add a comment to a post (user must be logged in)"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        post = Post.query.get(post_id)
        if post is None:
            return "Post not found", 404
        
        content = request.form.get('content')
        if content:
            new_comment = Comment(
                content=content,
                author=get_current_user(),
                post=post
            )
            db.session.add(new_comment)
            db.session.commit()
            flash('კომენტარი დამატებულია!', 'success')
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    
    # Admin panel
    @app.route('/admin')
    def admin():
        """Admin dashboard - shows posts waiting for approval"""
        user = get_current_user()
        if user is None or user.role != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        pending = Post.query.filter_by(is_published=False).all()
        return render_template('admin.html', pending_posts=pending)
    
    
    # Approve post
    @app.route('/admin/approve/<int:post_id>', methods=['POST', 'GET'])
    def approve_post(post_id):
        """Admin approves a post"""
        user = get_current_user()
        if user is None or user.role != 'admin':
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        post = Post.query.get(post_id)
        if post is None:
            return "Post not found", 404
        post.is_published = True
        db.session.commit()
        flash(f'პოსტი "{post.title}" დადასტურებულია!', 'success')
        return redirect(url_for('admin'))
    
    
    # Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Username and password required', 'danger')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Wrong username or password', 'danger')
        
        return render_template('login.html')
    
    
    # Register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Register page"""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            level = request.form.get('level', 'beginner')
            gender = request.form.get('gender', 'other')
            
            # Validate inputs
            if not username or not email or not password:
                flash('All fields are required', 'danger')
                return redirect(url_for('register'))
            
            # Check password length
            if len(password) < 8:
                flash('Password must be at least 8 characters', 'danger')
                return redirect(url_for('register'))
            
            # Check if username exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user is not None:
                flash('Username already taken', 'danger')
                return redirect(url_for('register'))
            
            # Check if email exists
            existing_email = User.query.filter_by(email=email).first()
            if existing_email is not None:
                flash('Email already registered', 'danger')
                return redirect(url_for('register'))
            
            # Set avatar based on gender
            if gender == 'male':
                avatar = '/static/images/avatar-male.png'
            elif gender == 'female':
                avatar = '/static/images/avatar-female.png'
            else:
                avatar = '/static/images/avatar-default.png'
            
            try:
                # Create user with hashed password
                new_user = User(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    level=level,
                    gender=gender,
                    profile_photo=avatar
                )
                
                db.session.add(new_user)
                db.session.commit()
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash('Error during registration', 'danger')
                return redirect(url_for('register'))
        
        return render_template('register.html')
    
    
    # Forgot password
    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        """Forgot password page - send reset link via email (simulated)"""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            user = User.query.filter_by(email=email).first()
            
            # Security: Always show same message whether email exists or not
            flash('თუ ეს ელ. მისამართი რეგისტრირებულია, პაროლის აღდგენის ბმული გამოგეგზავნებათ.', 'info')
            
            if user:
                try:
                    # Generate secure token
                    import secrets
                    reset_token = secrets.token_urlsafe(32)
                    session[f'reset_token_{user.id}'] = reset_token
                    session.permanent = True
                    
                    # In production, send email with reset link
                    # For demo, redirect directly
                    return redirect(url_for('reset_with_token', token=reset_token))
                except Exception as e:
                    flash('Error processing request', 'danger')
            
            return redirect(url_for('login'))
        
        return render_template('forgot_password.html')
    
    
    # Reset password
    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_with_token(token):
        """Reset password using token from forgot password"""
        try:
            # Find user with this token
            user_id = None
            for key in session.keys():
                if key.startswith('reset_token_') and session[key] == token:
                    user_id = int(key.split('_')[2])
                    break
            
            if not user_id:
                flash('ამ ბმულის ვადა გასულია ან ის არასწორია.', 'danger')
                return redirect(url_for('login'))
            
            user = User.query.get(user_id)
            if not user:
                flash('მომხმარებელი ვერ მოიძებნა.', 'danger')
                return redirect(url_for('login'))
            
            if request.method == 'POST':
                new_password = request.form.get('new_password', '')
                confirm_password = request.form.get('confirm_password', '')
                
                if not new_password or not confirm_password:
                    flash('ყველა ველი აუცილებელია.', 'danger')
                    return redirect(url_for('reset_with_token', token=token))
                
                if new_password != confirm_password:
                    flash('პაროლი არ ემთხვევა.', 'danger')
                    return redirect(url_for('reset_with_token', token=token))
                
                if len(new_password) < 8:
                    flash('Password must be at least 8 characters', 'danger')
                    return redirect(url_for('reset_with_token', token=token))
                
                # Update password
                user.password = generate_password_hash(new_password)
                db.session.commit()
                
                # Clear the reset token
                session.pop(f'reset_token_{user_id}', None)
                
                flash('პაროლი წარმატებით აღდგა! გთხოვთ შედით ახალი პაროლით.', 'success')
                return redirect(url_for('login'))
            
            return render_template('reset_with_token.html', token=token)
        except Exception as e:
            flash('Error processing reset', 'danger')
            return redirect(url_for('login'))
    
    
    # Change password
    @app.route('/change-password', methods=['GET', 'POST'])
    def reset_password():
        """Reset password for logged-in user"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        if request.method == 'POST':
            current_user = get_current_user()
            old_password = request.form.get('old_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not old_password or not new_password or not confirm_password:
                flash('All fields are required', 'danger')
                return redirect(url_for('reset_password'))
            
            # Verify old password
            if not check_password_hash(current_user.password, old_password):
                flash('ძველი პაროლი არასწორია.', 'danger')
                return redirect(url_for('reset_password'))
            
            # Check password length
            if len(new_password) < 8:
                flash('New password must be at least 8 characters', 'danger')
                return redirect(url_for('reset_password'))
            
            # Check if passwords match
            if new_password != confirm_password:
                flash('ახალი პაროლი არ ემთხვევა.', 'danger')
                return redirect(url_for('reset_password'))
            
            # Update password
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('პაროლი წარმატებით შეიცვალა!', 'success')
            return redirect(url_for('user_profile', username=current_user.username))
        
        return render_template('reset_password.html')
    
    # Like post
    @app.route('/post/<int:post_id>/like', methods=['POST'])
    def like_post(post_id):
        """User likes a post"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        
        try:
            post = Post.query.get(post_id)
            if post is None:
                return "Post not found", 404
            
            # Check if user already liked this post
            already_liked = Like.query.filter_by(post_id=post_id, author_id=user.id).first()
            
            if already_liked:
                # If already liked, remove the like (unlike)
                db.session.delete(already_liked)
                db.session.commit()
                flash('პოსტზე მოწონება გააუქმეთ!', 'info')
            else:
                # If not liked, add a like
                new_like = Like(
                    post_id=post_id,
                    author_id=user.id
                )
                db.session.add(new_like)
                if post.author_id != user.id:
                    db.session.add(Notification(
                        user_id=post.author_id,
                        sender_id=user.id,
                        post_id=post.id,
                        action='like',
                        message=f'{user.username}-მა მოიწონა თქვენი პოსტი: "{post.title}"'
                    ))
                db.session.commit()
                flash('პოსტი მოწონებულია!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error liking post', 'danger')
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    
    # Repost
    @app.route('/post/<int:post_id>/repost', methods=['POST'])
    def repost_post(post_id):
        """User reposts a post"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        
        try:
            post = Post.query.get(post_id)
            if post is None:
                return "Post not found", 404
            
            # Check if user already reposted this post
            already_reposted = Repost.query.filter_by(post_id=post_id, author_id=user.id).first()
            
            if already_reposted:
                # If already reposted, remove the repost
                db.session.delete(already_reposted)
                db.session.commit()
                flash('რეპოსტი წაშლილია.', 'info')
            else:
                # If not reposted, add a repost
                new_repost = Repost(
                    post_id=post_id,
                    author_id=user.id
                )
                db.session.add(new_repost)
                if post.author_id != user.id:
                    db.session.add(Notification(
                        user_id=post.author_id,
                        sender_id=user.id,
                        post_id=post.id,
                        action='repost',
                        message=f'{user.username}-მა გააზიარა თქვენი პოსტი: "{post.title}"'
                    ))
                db.session.commit()
                flash('თქვენ დაარეპოსტეთ პოსტი!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error reposting', 'danger')
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    # Logout
    @app.route('/logout')
    def logout():
        """User logout"""
        session.clear()
        flash('თქვენ გამოხვედით account-იდან.', 'info')
        return redirect(url_for('index'))    
    
    # User profile
    @app.route('/user/<username>')
    def user_profile(username):
        """Show user profile with their posts and reposts"""
        user = User.query.filter_by(username=username).first()
        if user is None:
            return "User not found", 404
        
        # Get user's own posts
        user_posts_all = Post.query.filter_by(author_id=user.id).all()
        user_posts = sorted(user_posts_all, key=lambda p: p.created_at, reverse=True)
        
        # Get user's reposts - find all reposts by this user
        user_reposts_all = Repost.query.filter_by(author_id=user.id).all()
        user_reposts = []
        for repost_obj in user_reposts_all:
            post_obj = Post.query.get(repost_obj.post_id)
            if post_obj:
                user_reposts.append(post_obj)
        user_reposts = sorted(user_reposts, key=lambda p: p.created_at, reverse=True)
        
        # Check if current user is following this user
        is_following = False
        is_mutual_follow = False
        current_user = get_current_user()
        if current_user and current_user.id != user.id:
            is_following = user in current_user.following
            follows_you = current_user in user.followers
            is_mutual_follow = is_following and follows_you
        
        return render_template('user_profile.html', user=user, posts=user_posts, reposts=user_reposts, is_following=is_following, is_mutual_follow=is_mutual_follow)
    
    
    # Update bio
    @app.route('/user/update-bio', methods=['POST'])
    def update_bio():
        """Update user's bio"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        bio = request.form.get('bio', '')
        
        user.bio = bio
        db.session.commit()
        flash('ბიო განახლებულია!', 'success')
        
        return redirect(url_for('user_profile', username=user.username))
    
    
    # Update level
    @app.route('/user/update-level', methods=['POST'])
    def update_level():
        """Update user's programming level"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        level = request.form.get('level', '')
        
        if level in ['beginner', 'junior', 'intermediate', 'senior']:
            user.level = level
            db.session.commit()
            flash('დონე განახლებულია!', 'success')
        else:
            flash('არასწორი დონე.', 'danger')
        
        return redirect(url_for('user_profile', username=user.username))
    
    
    # Upload photo
    @app.route('/user/upload-photo', methods=['POST'])
    def upload_photo():
        """Upload profile photo"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        
        # Check if file is in the request
        if 'photo' not in request.files:
            flash('ფოტო არ არის არჩეული.', 'danger')
            return redirect(url_for('user_profile', username=user.username))
        
        file = request.files['photo']
        
        if file.filename == '':
            flash('ფოტო არ არის არჩეული.', 'danger')
            return redirect(url_for('user_profile', username=user.username))
        
        if file and allowed_file(file.filename):
            # Check file size
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            file.seek(0)
            if file_length > MAX_FILE_SIZE:
                flash('File too large (max 5MB)', 'danger')
                return redirect(url_for('user_profile', username=user.username))
            
            try:
                # Save file to static/uploads directory
                upload_dir = os.path.join('static', 'uploads', 'profiles')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Generate unique filename
                filename = secure_filename(f"{user.id}_{file.filename}")
                filepath = os.path.join(upload_dir, filename)
                
                # Save file
                file.save(filepath)
                
                # Update user's profile_photo
                user.profile_photo = f'/{filepath.replace(chr(92), "/")}'
                db.session.commit()
                
                flash('ფოტო განახლებულია!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error uploading photo', 'danger')
        else:
            flash('Invalid file type. Allowed: jpg, jpeg, png, gif', 'danger')
        
        return redirect(url_for('user_profile', username=user.username))
    
    
    # Follow user
    @app.route('/user/<username>/follow', methods=['POST'])
    def follow_user(username):
        """Follow a user"""
        current_user = get_current_user()
        if current_user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        user_to_follow = User.query.filter_by(username=username).first()
        if user_to_follow is None:
            return "User not found", 404
        
        # Can't follow yourself
        if current_user.id == user_to_follow.id:
            flash('თქვენ არ შეგიძლიათ თქვენი თავის follow.', 'danger')
            return redirect(url_for('user_profile', username=username))
        
        # Check if already following
        if user_to_follow in current_user.following:
            flash('თქვენ უკვე აfolloweბთ ამ მომხმარებელს.', 'info')
        else:
            current_user.following.append(user_to_follow)
            if user_to_follow.id != current_user.id:
                db.session.add(Notification(
                    user_id=user_to_follow.id,
                    sender_id=current_user.id,
                    action='follow',
                    message=f'{current_user.username}-მა დაგაfollowათ'
                ))
            db.session.commit()
            flash(f'{user_to_follow.username}-Followed!', 'success')
        
        return redirect(url_for('user_profile', username=username))


    # Notifications
    @app.route('/notifications')
    def notifications():
        """List notifications for the current user and mark them read"""
        user = get_current_user()
        if user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        notifications = Notification.query.filter_by(user_id=user.id)\
                          .order_by(Notification.created_at.desc())\
                          .all()

        unread = [n for n in notifications if not n.is_read]
        for note in unread:
            note.is_read = True
        if unread:
            db.session.commit()

        return render_template('notifications.html', notifications=notifications)
    
    
    # Messages
    @app.route('/messages')
    def all_messages():
        """List all conversations for current user"""
        current_user = get_current_user()
        if current_user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        
        # Get all messages
        sent_messages = Message.query.filter_by(sender_id=current_user.id).all()
        received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
        all_messages = sent_messages + received_messages
        
        # Find unique users
        convo_user_ids = set()
        for msg in sent_messages:
            convo_user_ids.add(msg.receiver_id)
        for msg in received_messages:
            convo_user_ids.add(msg.sender_id)
        
        # Build conversations list
        conversations = []
        for user_id in convo_user_ids:
            other_user = User.query.get(user_id)
            if other_user:
                # Find last message with this user
                msgs_with_user = [m for m in all_messages if (m.sender_id == current_user.id and m.receiver_id == user_id) or (m.sender_id == user_id and m.receiver_id == current_user.id)]
                if msgs_with_user:
                    last_msg = sorted(msgs_with_user, key=lambda m: m.created_at)[-1]
                else:
                    last_msg = None
                
                # Count unread
                unread_count = 0
                for msg in received_messages:
                    if msg.sender_id == user_id and not msg.is_read:
                        unread_count = unread_count + 1
                
                conversations.append({
                    'user': other_user,
                    'last_message': last_msg,
                    'unread_count': unread_count
                })
        
        # Sort by latest message
        conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.min, reverse=True)
        return render_template('messages_list.html', conversations=conversations)


    # Message thread
    @app.route('/messages/<username>', methods=['GET', 'POST'])
    def message_thread(username):
        """Mutual followers can chat via direct messages"""
        current_user = get_current_user()
        if current_user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        other_user = User.query.filter_by(username=username).first()
        if other_user is None:
            return "User not found", 404

        if other_user.id == current_user.id:
            flash('შეტყობინების გაგზავნა საკუთარ თავთან შეუძლებელია.', 'warning')
            return redirect(url_for('user_profile', username=username))

        follows_other = other_user in current_user.following
        follows_current = current_user in other_user.following
        if not (follows_other and follows_current):
            flash('შეტყობინება ხელმისაწვდომია მხოლოდ მოხმარებელთან რომელიც უკან გაfollow-ებთ', 'warning')
            return redirect(url_for('user_profile', username=username))

        if request.method == 'POST':
            content = request.form.get('content', '').strip()
            if content:
                msg = Message(sender_id=current_user.id, receiver_id=other_user.id, content=content)
                db.session.add(msg)
                db.session.commit()
                flash('შეტყობინება გაგზავნილია!', 'success')
            else:
                flash('შეტყობინება ცარიელია.', 'danger')
            return redirect(url_for('message_thread', username=other_user.username))

        messages = Message.query.filter_by(sender_id=current_user.id, receiver_id=other_user.id).all()
        messages2 = Message.query.filter_by(sender_id=other_user.id, receiver_id=current_user.id).all()
        messages = messages + messages2
        messages = sorted(messages, key=lambda m: m.created_at)

        unread = [m for m in messages if m.receiver_id == current_user.id and not m.is_read]
        for m in unread:
            m.is_read = True
        if unread:
            db.session.commit()

        return render_template('messages_thread.html', other=other_user, messages=messages)


    # View followers
    @app.route('/user/<username>/followers')
    def view_followers(username):
        """View user's followers list"""
        user = User.query.filter_by(username=username).first()
        if user is None:
            return "User not found", 404
        followers = user.followers
        return render_template('followers_list.html', user=user, followers=followers)


    # View following
    @app.route('/user/<username>/following')
    def view_following(username):
        """View user's following list"""
        user = User.query.filter_by(username=username).first()
        if user is None:
            return "User not found", 404
        following = user.following
        return render_template('following_list.html', user=user, following=following)


    # Follow back
    @app.route('/user/<username>/follow-back', methods=['POST'])
    def follow_back(username):
        """Follow back a user from notification"""
        current_user = get_current_user()
        if current_user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        user_to_follow = User.query.filter_by(username=username).first()
        if user_to_follow is None:
            return "User not found", 404

        if current_user.id == user_to_follow.id:
            flash('თქვენ არ შეგიძლიათ თქვენი თავის follow.', 'danger')
            return redirect(url_for('notifications'))

        if user_to_follow not in current_user.following:
            current_user.following.append(user_to_follow)
            db.session.add(Notification(
                user_id=user_to_follow.id,
                sender_id=current_user.id,
                action='follow',
                message=f'{current_user.username}-მა დაგაfollowათ'
            ))
            db.session.commit()
            flash(f'{user_to_follow.username}-Follow back!', 'success')
        else:
            flash('თქვენ უკვე აfolloweბთ ამ მომხმარებელს.', 'info')

        return redirect(url_for('notifications'))


    # Unfollow user
    @app.route('/user/<username>/unfollow', methods=['POST'])
    def unfollow_user(username):
        """Unfollow a user"""
        current_user = get_current_user()
        if current_user is None:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        user_to_unfollow = User.query.filter_by(username=username).first()
        if user_to_unfollow is None:
            return "User not found", 404
        
        # Check if following
        if user_to_unfollow in current_user.following:
            current_user.following.remove(user_to_unfollow)
            db.session.commit()
            flash(f'{user_to_unfollow.username}-Unfollowed.', 'success')
        else:
            flash('Unfollowed.', 'info')
        
        return redirect(url_for('user_profile', username=username))