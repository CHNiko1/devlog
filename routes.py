"""
All routes for the DevLog app
These are the different pages and actions users can do
"""

import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

from models import db, User, Post, Comment, Like, Repost
from auth import login_required, admin_required, get_current_user


def setup_routes(app):
    """
    This function sets up all the routes for the app
    Call this function in app.py to register all routes
    """

    # ============ DELETE POST ============
    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    @login_required
    def delete_post(post_id):
        """Delete a post (author or admin only)"""
        post = Post.query.get_or_404(post_id)
        user = get_current_user()

        if post.author_id != user.id and user.role != 'admin':
            flash('თქვენ არ გაქვთ ამ პოსტის წაშლის უფლება.', 'danger')
            return redirect(url_for('post_detail', post_id=post_id))

        db.session.delete(post)
        db.session.commit()
        flash('პოსტი წარმატებით წაიშალა.', 'success')

        if user.role == 'admin':
            return redirect(url_for('admin'))
        return redirect(url_for('user_profile', username=user.username))


    """
    This function sets up all the routes for the app
    Call this function in app.py to register all routes
    """
    
    # ============ HOME PAGE ============
    @app.route('/')
    def index():
        """Home page - shows featured posts"""
        posts = Post.query.filter_by(is_published=True)\
                         .order_by(Post.created_at.desc())\
                         .limit(6)\
                         .all()
        return render_template('index.html', posts=posts)
    
    
    # ============ VIEW ALL POSTS ============
    @app.route('/posts')
    def posts():
        """All posts page with search and filters"""
        q = request.args.get('q', '')
        language = request.args.get('language', '')
        level = request.args.get('level', '')
        
        # Start with published posts
        query = Post.query.filter_by(is_published=True)
        
        # If user searched for something, search in title and content
        if q:
            query = query.filter(
                (Post.title.ilike(f'%{q}%')) | (Post.content.ilike(f'%{q}%'))
            )
        
        # Filter by language if selected
        if language:
            query = query.filter_by(language=language)
        
        # Filter by level if selected
        if level:
            query = query.filter_by(level=level)
        
        # Get posts, newest first
        posts_list = query.order_by(Post.created_at.desc()).all()
        
        # Send filter info to template so we can show what's filtered
        active_filters = {
            'q': q,
            'language': language,
            'level': level
        }
        
        return render_template('posts.html', posts=posts_list, filters=active_filters)
    
    
    # ============ CLEAR FILTERS ============
    @app.route('/posts/clear-filters')
    def clear_filters():
        """Clear all filters and show all posts"""
        # Redirect back to posts page with no filters
        return redirect(url_for('posts'))
    
    # ============ SINGLE POST VIEW ============
    @app.route('/post/<int:post_id>')
    def post_detail(post_id):
        """View a single post with comments"""
        post = Post.query.get_or_404(post_id)
        return render_template('post_detail.html', post=post)
    
    
    # ============ CREATE POST ============
    @app.route('/create-post', methods=['GET', 'POST'])
    @login_required
    def create_post():
        """Create a new post (user must be logged in)"""
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            language = request.form.get('language')
            level = request.form.get('level')
            
            # Handle photo upload
            photo_filename = None
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename != '':
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
        
        return render_template('create_post.html')
    
    
    # ============ MY POSTS ============
    @app.route('/my-posts')
    @login_required
    def my_posts():
        """Redirect to user's profile page"""
        user = get_current_user()
        return redirect(url_for('user_profile', username=user.username))
    
    
    # ============ ADD COMMENT ============
    @app.route('/post/<int:post_id>/comment', methods=['POST'])
    @login_required
    def add_comment(post_id):
        """Add a comment to a post (user must be logged in)"""
        post = Post.query.get_or_404(post_id)
        
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
    
    
    # ============ ADMIN PANEL ============
    @app.route('/admin')
    @admin_required
    def admin():
        """Admin dashboard - shows posts waiting for approval"""
        pending = Post.query.filter_by(is_published=False).all()
        return render_template('admin.html', pending_posts=pending)
    
    
    # ============ APPROVE POST (ADMIN ONLY) ============
    @app.route('/admin/approve/<int:post_id>', methods=['POST', 'GET'])
    @admin_required
    def approve_post(post_id):
        """Admin approves a post"""
        post = Post.query.get_or_404(post_id)
        post.is_published = True
        db.session.commit()
        flash(f'პოსტი "{post.title}" დადასტურებულია!', 'success')
        return redirect(url_for('admin'))
    
    
    # ============ LOGIN ============
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Find user by username
            user = User.query.filter_by(username=username).first()
            
            # Check if user exists and password is correct
            if user and user.password == password:
                session['user_id'] = user.id
                # Check if this is the first login
                if request.args.get('first_login'):
                    flash('თქვენ წარმატებით დარეგისტრირდით!', 'success')
                else:
                    flash(f'კეთილი იყოს თქვენი დაბრუნება, {user.username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('მომხმარებლის სახელი ან პაროლი არასწორია.', 'danger')
        
        return render_template('login.html')
    
    
    # ============ REGISTER ============
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration page"""
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Check if username already exists
            if User.query.filter_by(username=username).first():
                flash('ეს მომხმარებლის სახელი დაკავებულია.', 'danger')
                return redirect(url_for('register'))
            
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('ეს ელ. მისამართი უკვე რეგისტრირებულია.', 'danger')
                return redirect(url_for('register'))
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password=password  # Note: In production, hash this!
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('რეგისტრაცია წარმატებით გაიარეთ !', 'success')
            return redirect(url_for('login', first_login='true'))
        
        return render_template('register.html')
    
    
    
    # ============ LIKE POST ============
    @app.route('/post/<int:post_id>/like', methods=['POST'])
    @login_required
    def like_post(post_id):
        """User likes a post"""
        post = Post.query.get_or_404(post_id)
        user = get_current_user()
        
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
            db.session.commit()
            flash('პოსტი მოწონებულია!', 'success')
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    
    # ============ REPOST ============
    @app.route('/post/<int:post_id>/repost', methods=['POST'])
    @login_required
    def repost_post(post_id):
        """User reposts a post"""
        post = Post.query.get_or_404(post_id)
        user = get_current_user()
        
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
            db.session.commit()
            flash('თქვენ დაარეპოსტეთ პოსტი!', 'success')
        
        return redirect(url_for('post_detail', post_id=post_id))
    
    # ============ LOGOUT ============
    @app.route('/logout')
    def logout():
        """User logout"""
        session.clear()
        flash('თქვენ გამოხვედით account-იდან.', 'info')
        return redirect(url_for('index'))    
    
    # ============ USER PROFILE PAGE ============
    @app.route('/user/<username>')
    def user_profile(username):
        """Show user profile with their posts and reposts"""
        user = User.query.filter_by(username=username).first_or_404()
        
        # Get user's own posts
        user_posts = Post.query.filter_by(author_id=user.id)\
                               .order_by(Post.created_at.desc())\
                               .all()
        
        # Get user's reposts - find all posts that this user has reposted
        user_reposts = db.session.query(Post)\
                                  .join(Repost, Post.id == Repost.post_id)\
                                  .filter(Repost.author_id == user.id)\
                                  .order_by(Repost.created_at.desc())\
                                  .all()
        
        # Check if current user is following this user
        is_following = False
        current_user = get_current_user()
        if current_user and current_user.id != user.id:
            is_following = user in current_user.following
        
        return render_template('user_profile.html', user=user, posts=user_posts, reposts=user_reposts, is_following=is_following)
    
    
    # ============ UPDATE BIO ============
    @app.route('/user/update-bio', methods=['POST'])
    @login_required
    def update_bio():
        """Update user's bio"""
        user = get_current_user()
        bio = request.form.get('bio', '')
        
        user.bio = bio
        db.session.commit()
        flash('ბიო განახლებულია!', 'success')
        
        return redirect(url_for('user_profile', username=user.username))
    
    
    # ============ UPLOAD PROFILE PHOTO ============
    @app.route('/user/upload-photo', methods=['POST'])
    @login_required
    def upload_photo():
        """Upload profile photo"""
        user = get_current_user()
        
        # Check if file is in the request
        if 'photo' not in request.files:
            flash('ფოტო არ არის არჩეული.', 'danger')
            return redirect(url_for('user_profile', username=user.username))
        
        file = request.files['photo']
        
        if file.filename == '':
            flash('ფოტო არ არის არჩეული.', 'danger')
            return redirect(url_for('user_profile', username=user.username))
        
        if file:
            # Save file to static/uploads directory
            import os
            from werkzeug.utils import secure_filename
            
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
        
        return redirect(url_for('user_profile', username=user.username))
    
    
    # ============ FOLLOW USER ============
    @app.route('/user/<username>/follow', methods=['POST'])
    @login_required
    def follow_user(username):
        """Follow a user"""
        user_to_follow = User.query.filter_by(username=username).first_or_404()
        current_user = get_current_user()
        
        # Can't follow yourself
        if current_user.id == user_to_follow.id:
            flash('თქვენ არ შეგიძლიათ თქვენი თავის follow.', 'danger')
            return redirect(url_for('user_profile', username=username))
        
        # Check if already following
        if user_to_follow in current_user.following:
            flash('თქვენ უკვე აfolloweბთ ამ მომხმარებელს.', 'info')
        else:
            current_user.following.append(user_to_follow)
            db.session.commit()
            flash(f'{user_to_follow.username}-Followed!', 'success')
        
        return redirect(url_for('user_profile', username=username))
    
    
    # ============ UNFOLLOW USER ============
    @app.route('/user/<username>/unfollow', methods=['POST'])
    @login_required
    def unfollow_user(username):
        """Unfollow a user"""
        user_to_unfollow = User.query.filter_by(username=username).first_or_404()
        current_user = get_current_user()
        
        # Check if following
        if user_to_unfollow in current_user.following:
            current_user.following.remove(user_to_unfollow)
            db.session.commit()
            flash(f'{user_to_unfollow.username}-Unfollowed.', 'success')
        else:
            flash('Unfollowed.', 'info')
        
        return redirect(url_for('user_profile', username=username))