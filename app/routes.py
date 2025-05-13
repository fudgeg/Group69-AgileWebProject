import os 
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from .models import db, MediaEntry, User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models import db, MediaEntry, Book, Movie, TVShow, Music
from app.utils import get_media_type_breakdown, get_user_media_identity
from collections import Counter

main = Blueprint('main', __name__)


@main.route('/')
def welcome():
    return render_template('welcome.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("All fields are required","error")
            return redirect(url_for('main.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in',"caution")
            return redirect(url_for('main.login'))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print(f"[SIGNUP] New user created: {user.name} | {user.email}")
        flash('Signup successful. Please log in')
        return redirect(url_for('main.login'))

    return render_template('signup.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the fields are empty
        if not email or not password:
            flash("Email and password are required.", 'error')
            return redirect(url_for('main.login'))

        # Check if the user exists
        user = User.query.filter_by(email=email).first()

        # Validate password
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("You are now logged in.")
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')


@main.route('/logout')
def logout():
    session.clear()  # Clear all session data to avoid leftover messages
    flash('You have been logged out',"caution")
    return redirect(url_for('main.welcome'))


@main.route('/home')
def home():
    user_id = session.get('user_id')
    print(f"[DEBUG] Session user_id: {user_id}")

    if not user_id:
        flash("You must be logged in to view this page.","error")
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    print(f"[DEBUG] User from DB: {user}")

    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))

    # Query the most recent media entries 
    recent_entries = MediaEntry.query.order_by(MediaEntry.id.desc()).limit(5).all()

    # Get media entries created by the user's friends 
    friend_ids = [f.id for f in user.friends]
    friend_entries = (
        MediaEntry.query
        .filter(MediaEntry.user_id.in_(friend_ids))
        .order_by(MediaEntry.id.desc())
        .limit(5)
        .all()
    )

    return render_template('home.html',
                           user=user,
                           recent_entries=recent_entries,
                           friend_entries=friend_entries)


@main.route('/friends', methods=['GET', 'POST'])
def friends():
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to view friends.","error")
        return redirect(url_for('main.login'))

    # Handle Add-by-Username form
    if request.method == 'POST' and 'username_search' in request.form:
        name_query = request.form['username_search'].strip()
        if name_query:
            other = User.query.filter_by(name=name_query).first()
            if other and other.id != user.id and other not in user.friends:
                user.friends.append(other)
                other.friends.append(user)
                db.session.commit()
                flash(f"Friend request sent to {other.name}!", "success")
        return redirect(url_for('main.friends'))

    # Confirmed friends
    friends = user.friends

    # Recommended connections
    recommended = User.query.filter(
        User.id != user.id,
        ~User.id.in_([f.id for f in friends])
    ).all()

    # Fetch this user's own media entries for sharing
    user_media = MediaEntry.query.filter_by(user_id=user.id).all()

    return render_template('friends.html',
                           user=user,
                           friends=friends,
                           recommended=recommended,
                           user_media=user_media)


@main.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    user = User.query.get(session.get('user_id'))
    friend = User.query.get(friend_id)

    if not user or not friend or friend == user:
        flash("Invalid request.","error")
        return redirect(url_for('main.friends'))

    if friend in user.friends:
        flash("You're already friends.","caution")
        return redirect(url_for('main.friends'))

    user.friends.append(friend)
    friend.friends.append(user)
    db.session.commit()

    flash(f"You are now friends with {friend.name}!")
    return redirect(url_for('main.friends'))


@main.route('/share_media', methods=['POST'])
def share_media():
    """Share one of the current user's media entries with a friend."""
    user      = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to share media.", "error")
        return redirect(url_for('main.login'))

    media_id  = request.form.get('media_id', type=int)
    friend_id = request.form.get('friend_id', type=int)
    media     = MediaEntry.query.get(media_id)
    friend    = User.query.get(friend_id)

    # Validate inputs & friendship
    if not media or not friend or friend not in user.friends:
        flash("Invalid share request.", "error")
        return redirect(url_for('main.friends'))

    # Build a shared title so it can be flagged in templates
    shared_title = f"{media.title} (shared)"

    # Prevent duplicate shares of the same shared entry
    exists = MediaEntry.query.filter_by(
        user_id=friend.id,
        media_type=media.media_type,
        title=shared_title
    ).first()

    if exists:
        flash(f"{friend.name} already has “{media.title}”", "caution")
    else:
        new_entry = MediaEntry(
            media_type=media.media_type,
            title=shared_title,
            user_id=friend.id
        )
        db.session.add(new_entry)
        db.session.commit()
        flash(f"Shared “{media.title}” with {friend.name}", "success")

    return redirect(url_for('main.friends'))


@main.route('/upload', methods=['GET', 'POST'])
def upload_page():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to upload media.", "error")
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        # these names match your upload.html:
        media_type = request.form.get('media_type')
        title      = request.form.get('title')
        rating     = request.form.get('rating')  or None
        comment    = request.form.get('comment') or None

        def parse_date(val):
            return datetime.strptime(val, '%Y-%m-%d') if val else None

        # pick the right genre field
        if media_type == 'book':
            genre = request.form.get('book_genre')
        elif media_type == 'movie':
            genre = request.form.get('movie_genre')
        elif media_type == 'tv_show':
            genre = request.form.get('tvshow_genre')
        elif media_type == 'music':
            genre = request.form.get('music_genre')
        else:
            genre = None

        # normalize genre
        genre = (genre or "").strip().title() or None

        # validate that we have at least type and title
        if not media_type or not title:
            flash("Please select a media type and enter a title.", "error")
            return redirect(url_for('main.upload_page'))

        # Construct the correct subclass based on media_type
        if media_type == 'book':
            entry = Book(
                media_type='book',
                title=title,
                rating=rating,
                comments=comment,
                genre=genre,
                author=request.form.get('author'),
                date_started=parse_date(request.form.get('date_started')),
                date_finished=parse_date(request.form.get('date_finished')),
                status=request.form.get('status'),
                user_id=user_id
            )
        elif media_type == 'movie':
            entry = Movie(
                media_type='movie',
                title=title,
                rating=rating,
                comments=comment,
                genre=genre,
                consumed_date=parse_date(request.form.get('watched_date')),
                user_id=user_id
            )
        elif media_type == 'tv_show':
            entry = TVShow(
                media_type='tv_show',
                title=title,
                rating=rating,
                comments=comment,
                genre=genre,
                watched_date=parse_date(request.form.get('watched_date')),
                user_id=user_id
            )
        elif media_type == 'music':
            entry = Music(
                media_type='music',
                title=title,
                rating=rating,
                comments=comment,
                genre=genre,
                artist=request.form.get('artist'),
                user_id=user_id
            )
        else:
            flash("Invalid media type.", "error")
            return redirect(url_for('main.upload_page'))

        db.session.add(entry)
        db.session.commit()
        flash("Media entry added successfully!", "success")
        return redirect(url_for('main.upload_page'))

    # GET: show only this user's entries
    entries = MediaEntry.query.filter_by(user_id=user_id).all()
    return render_template('upload.html', entries=entries)


@main.route('/settings')
def settings():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to access settings.", "error")
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))

    profile_picture_url = url_for('static', filename=f'media/{user.profile_picture}')
    return render_template('settings.html', user=user, profile_picture_url=profile_picture_url)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your profile picture.", "error")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))
    
    # Check if a file is uploaded
    if 'profile_picture' not in request.files:
        flash("No file selected. Please try again.", "error")
        return redirect(url_for('main.settings'))
    
    file = request.files['profile_picture']
    
    # Check if the file is valid
    if file.filename == '' or not allowed_file(file.filename):
        flash("Invalid file type. Please upload a PNG, JPG, JPEG, or GIF file.", "error")
        return redirect(url_for('main.settings'))
    
    # Secure the filename and save the file
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.static_folder, 'media')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Update the user's profile picture
    user.profile_picture = filename
    db.session.commit()

    flash("Profile picture updated successfully.")
    return redirect(url_for('main.settings'))


@main.route('/update_username', methods=['POST'])
def update_username():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your username.","error")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))

    # Get the new username and password from the form
    new_username = request.form.get('username').strip()
    password = request.form.get('password').strip()
    
    # Verify password
    if not user.check_password(password):
        flash("Incorrect password. Please try again.","error")
        return redirect(url_for('main.settings'))
    
    # Check if the new username is valid
    if not new_username:
        flash("Username cannot be empty.","error")
        return redirect(url_for('main.settings'))
    
    # Update the username
    user.name = new_username
    db.session.commit()
    
    # Provide user feedback
    flash("Username updated successfully.")
    return redirect(url_for('main.settings'))


@main.route('/update_email', methods=['POST'])
def update_email():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your email.","error")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))

    # Get the new email and password from the form
    new_email = request.form.get('email').strip().lower()
    password = request.form.get('password').strip()
    
    # Verify password
    if not user.check_password(password):
        flash("Incorrect password. Please try again.","error")
        return redirect(url_for('main.settings'))
    
    # Check if the new email is valid
    if not new_email:
        flash("Email cannot be empty.","error")
        return redirect(url_for('main.settings'))
    
    # Check if the new email is already taken
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        flash("This email is already registered. Please use a different email.","error")
    
    # Update the email
    user.email = new_email
    db.session.commit()
    
    # Log the user out to force re-login with the new email
    session.clear()
    flash("Email updated successfully. Please log in with your new email.","caution")
    return redirect(url_for('main.login'))


@main.route('/update_password', methods=['POST'])
def update_password():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your password.","error")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))

    # Get the current and new passwords from the form
    current_password = request.form.get('current_password').strip()
    new_password = request.form.get('new_password').strip()
    confirm_password = request.form.get('confirm_password').strip()
    
    # Verify current password
    if not user.check_password(current_password):
        flash("Incorrect current password. Please try again.", "error")
        return redirect(url_for('main.settings'))
    
    # Check if the new password matches the confirmation
    if new_password != confirm_password:
        flash("New passwords do not match. Please try again.", "error")
        return redirect(url_for('main.settings'))
    
    # Update the password
    user.set_password(new_password)
    db.session.commit()
    
    # Log the user out to force re-login with the new email
    session.clear()
    flash("Password updated successfully. Please log in with your new email.","caution")
    return redirect(url_for('main.login'))
    


@main.route('/delete_account', methods=['POST'])
def delete_account():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to delete your account.","error")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))

    # Verify password
    delete_password = request.form.get('delete_password').strip()
    if not user.check_password(delete_password):
        flash("Incorrect password. Please try again.", "error")
        return redirect(url_for('main.settings'))
    
    # Remove all media entries associated with the user
    MediaEntry.query.filter_by(user_id=user.id).delete()
    
    # Remove the user
    db.session.delete(user)
    db.session.commit()
    
    # Clear the session and redirect to the welcome page
    session.clear()
    flash("Your account has been permanently deleted.", "caution")
    return redirect(url_for('main.welcome'))

@main.route('/foryou')
def for_you():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to access this page.", "error")
        return redirect(url_for('main.login'))

    def get_genre_counts(queryset):
        counts = {}
        for entry in queryset:
            if entry.genre:
                counts[entry.genre] = counts.get(entry.genre, 0) + 1
        return counts

    books = Book.query.filter_by(user_id=user_id).all()
    movies = Movie.query.filter_by(user_id=user_id).all()
    tv_shows = TVShow.query.filter_by(user_id=user_id).all()
    music = Music.query.filter_by(user_id=user_id).all()

    media_counts = {
        "Books": len(books),
        "Movies": len(movies),
        "TV Shows": len(tv_shows),
        "Music": len(music),
    }
    
    combined_screen = movies + tv_shows
    genre_breakdowns = {
        "Books": get_genre_counts(books),
        #"Movies": get_genre_counts(movies),
        #"TV Shows": get_genre_counts(tv_shows),
        "Tv&Movies": get_genre_counts(combined_screen),  # combined category tv and movies 
        "Music": get_genre_counts(music),
    }
    
    
    
    identity_label = get_user_media_identity(media_counts)
    
    return render_template("foryou.html", identity=identity_label, media_counts=media_counts, genre_breakdowns=genre_breakdowns)
