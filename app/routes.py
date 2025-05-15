import os, json, uuid
from datetime import datetime
from collections import Counter

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    current_app,
    jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Single import block for all models
from app.models import (
    db,
    MediaEntry,
    User,
    Book,
    Movie,
    TVShow,
    Music,
    FriendRequest,
    UserActivity,
    MediaSnapshot
)
from app.utils import get_media_type_breakdown, get_user_media_identity

main = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def welcome():
    return render_template('welcome.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('full_name')
        email    = request.form.get('email')
        password = request.form.get('password')
        if not name or not email or not password:
            flash("All fields are required", "error")
            return redirect(url_for('main.signup'))
        existing_username = User.query.filter_by(name=name).first()
        if existing_username:
            flash("Username already taken. Please choose a different one.", "error")
            return redirect(url_for('main.signup'))
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in', "caution")
            return redirect(url_for('main.login'))
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful. Please log in')
        return redirect(url_for('main.login'))
    return render_template('signup.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            flash("Email and password are required.", 'error')
            return redirect(url_for('main.login'))
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("You are now logged in.")
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@main.route('/logout')
def logout():
    # only log out the user
    session.clear()
    flash('You have been logged out', "caution")
    return redirect(url_for('main.welcome'))

@main.route('/home')
def home():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to view this page.", "error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))

    # MOST RECENT ACTIVITY: your own uploads 
    db_entries = (
        MediaEntry.query
        .filter_by(user_id=user.id)
        .order_by(MediaEntry.id.desc())
        .limit(10)
        .all()
    )
    recent_entries = [m for m in db_entries if "(shared)" not in m.title][:5]

    # Add shared items to recent entries
    all_shares = session.get('your_shares', [])
    mine = [s for s in all_shares if s.get('sharer_id') == user.id]

    if mine:
        class TempEntry:
            def __init__(self, media_type, title, sharer_name, recipient_name):
                self.media_type = media_type
                self.title = title + " (shared)"
                self.sharer_name = sharer_name
                self.recipient_name = recipient_name

        for share in reversed(mine):
            sharer = User.query.get(share['sharer_id'])
            recipient = User.query.get(share.get('recipient_id'))  # Get the actual recipient

            # Avoid self-sharing in the wrong context
            if sharer and recipient and recipient.id != sharer.id:
                recent_entries.insert(0, TempEntry(
                    share['media_type'],
                    share['title'],
                    sharer.name,
                    recipient.name
                ))

            # If the recipient is the current user (self-share), still include but adjust wording
            elif sharer and recipient and recipient.id == user.id:
                recent_entries.insert(0, TempEntry(
                    share['media_type'],
                    share['title'],
                    "You",
                    "yourself"
                ))

        recent_entries = recent_entries[:5]



    # LATEST FRIENDS ACTIVITY: entries shared to you by friends
    friend_entries = (
        MediaEntry.query
        .filter_by(user_id=user.id)
        .filter(MediaEntry.title.contains('(shared)'))
        .order_by(MediaEntry.id.desc())
        .limit(5)
        .all()
    )

    # Add the friend’s name who shared it and skip any we can’t match
    friend_ids   = [f.id for f in user.friends]
    real_friends = []
    for entry in friend_entries:
        clean = entry.title.rsplit(' (shared)', 1)[0]
        sharer = (
            MediaEntry.query
            .filter(
                MediaEntry.user_id.in_(friend_ids),
                MediaEntry.media_type == entry.media_type,
                MediaEntry.title == clean
            )
            .order_by(MediaEntry.id.desc())
            .first()
        )
        if sharer:
            entry.sharer_name = sharer.user.name
            real_friends.append(entry)
    friend_entries = real_friends

    return render_template(
        'home.html',
        user=user,
        recent_entries=recent_entries,
        friend_entries=friend_entries
    )


@main.route('/friends', methods=['GET', 'POST'])
def friends():
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to view friends.","error")
        return redirect(url_for('main.login'))

    # Handle Add Friend by name
    if request.method == 'POST' and 'username_search' in request.form:
        name_query = request.form['username_search'].strip()
        if name_query:
            other = User.query.filter_by(name=name_query).first()
            if other and other.id != user.id and other not in user.friends:
                user.friends.append(other)
                other.friends.append(user)
                db.session.commit()
        return redirect(url_for('main.friends'))

    # Fetch the current user's friends
    friends = user.friends

    # Fetch recommended connections (all users except current user and their friends)
    recommended = User.query.filter(
        User.id != user.id,
        ~User.id.in_([f.id for f in user.friends])
    ).all()

    # Fetch the user's own media entries for sharing
    user_media = MediaEntry.query.filter_by(user_id=user.id).order_by(MediaEntry.media_type, MediaEntry.title).all()

    return render_template('friends.html', user=user, friends=friends, recommended=recommended,user_media=user_media)


@main.route('/search', methods=['GET'])
def search_users():
    # Ensure the user is logged in
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to search for friends.", "error")
        return redirect(url_for('main.login'))

    # Get the search query from the URL
    query = request.args.get('query', '').strip()
    
    # Make sure the query is not empty
    if not query:
        flash("Please enter a valid username to search.", "error")
        return redirect(url_for('main.friends'))

    # Fetch users whose names contain the search term, excluding the current user and existing friends
    search_results = User.query.filter(
        User.name.ilike(f"%{query}%"),
        User.id != user.id,
        ~User.id.in_([f.id for f in user.friends])
    ).all()

    # Render the search results
    return render_template('friends_search.html', user=user, search_results=search_results)

@main.route('/send_friend_request/<int:receiver_id>', methods=['POST'])
def send_friend_request(receiver_id):
    user = User.query.get(session.get('user_id'))
    receiver = User.query.get(receiver_id)

    if not user or not receiver or user == receiver:
        flash("Invalid friend request.", "error")
        return redirect(url_for('main.friends'))

    # Check if a request already exists
    existing_request = FriendRequest.query.filter_by(
        sender_id=user.id,
        receiver_id=receiver.id
    ).first()

    if existing_request:
        flash("Friend request already sent.", "caution")
        return redirect(url_for('main.friends'))

    # Create a new friend request
    friend_request = FriendRequest(sender_id=user.id, receiver_id=receiver.id)
    db.session.add(friend_request)
    db.session.commit()

    flash("Friend request sent, awaiting approval.", "success")
    return redirect(url_for('main.friends'))


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
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to share media.", "error")
        return redirect(url_for('main.login'))

    media_id  = request.form.get('media_id', type=int)
    friend_id = request.form.get('friend_id', type=int)
    media     = MediaEntry.query.get(media_id)
    friend    = User.query.get(friend_id)

    if not media or not friend or friend not in user.friends:
        flash("Invalid share request.", "error")
        return redirect(url_for('main.friends'))

    shared_title = f"{media.title} (shared)"
    exists = MediaEntry.query.filter_by(
        user_id=friend.id,
        media_type=media.media_type,
        title=shared_title
    ).first()

    if exists:
        flash(f"{friend.name} already has “{media.title}”", "caution")
    else:
        # Insert into friend's list
        friend_entry = MediaEntry(
            media_type=media.media_type,
            title=shared_title,
            user_id=friend.id
        )
        db.session.add(friend_entry)
        db.session.commit()

        # Record your share in session (with sharer_id and recipient_id)
        shares = session.get('your_shares', [])
        shares.append({
            'media_type': media.media_type,
            'title':      media.title,
            'sharer_id':  user.id,
            'recipient_id': friend.id
        })
        session['your_shares'] = shares

        flash(f"Shared “{media.title}” with {friend.name}", "success")

    return redirect(url_for('main.friends'))


@main.route('/upload', methods=['GET', 'POST'])
def upload_page():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to upload media.", "error")
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        media_type = request.form.get('media_type')
        title      = request.form.get('title')
        rating     = request.form.get('rating') or None
        comment    = request.form.get('comment') or None

        def parse_date(val):
            return datetime.strptime(val, '%Y-%m-%d') if val else None

        if media_type == 'book':
            entry = Book(
                media_type='book',
                title=title,
                rating=rating,
                comments=comment,
                genre=(request.form.get('book_genre') or "").title() or None,
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
                genre=(request.form.get('movie_genre') or "").title() or None,
                consumed_date=parse_date(request.form.get('watched_date')),
                user_id=user_id
            )
        elif media_type == 'tv_show':
            entry = TVShow(
                media_type='tv_show',
                title=title,
                rating=rating,
                comments=comment,
                genre=(request.form.get('tvshow_genre') or "").title() or None,
                watched_date=parse_date(request.form.get('watched_date')),
                user_id=user_id
            )
        elif media_type == 'music':
            entry = Music(
                media_type='music',
                title=title,
                rating=rating,
                comments=comment,
                genre=(request.form.get('music_genre') or "").title() or None,
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

@main.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your profile picture.", "error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))
    if 'profile_picture' not in request.files:
        flash("No file selected. Please try again.", "error")
        return redirect(url_for('main.settings'))
    file = request.files['profile_picture']
    if file.filename == '' or not allowed_file(file.filename):
        flash("Invalid file type. Please upload a PNG, JPG, JPEG, or GIF file.", "error")
        return redirect(url_for('main.settings'))
    filename = secure_filename(file.filename)
    upload_folder = os.path.join(current_app.static_folder, 'media')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    user.profile_picture = filename
    db.session.commit()
    flash("Profile picture updated successfully.")
    return redirect(url_for('main.settings'))
@main.route('/update_username', methods=['POST'])
def update_username():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your username.","error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))
    new_username = request.form.get('username').strip()
    password     = request.form.get('password').strip()
    existing_username = User.query.filter_by(name=new_username).first()
    if existing_username:
        flash("Username already taken. Please choose a different one.", "error")
        return redirect(url_for('main.settings'))
    if not user.check_password(password):
        flash("Incorrect password. Please try again.","error")
        return redirect(url_for('main.settings'))
    if not new_username:
        flash("Username cannot be empty.","error")
        return redirect(url_for('main.settings'))
    
    old_username = user.name
    user.name = new_username
    db.session.commit()

    # Log the change
    activity = UserActivity(user_id=user.id, activity_type="username_change", old_value=old_username, new_value=new_username)
    db.session.add(activity)
    db.session.commit()

    flash("Username updated successfully.")
    return redirect(url_for('main.settings'))
@main.route('/update_email', methods=['POST'])
def update_email():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your email.","error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))
    new_email = request.form.get('email').strip().lower()
    password  = request.form.get('password').strip()
    if not user.check_password(password):
        flash("Incorrect password. Please try again.","error")
        return redirect(url_for('main.settings'))
    if not new_email:
        flash("Email cannot be empty.","error")
        return redirect(url_for('main.settings'))
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        flash("This email is already registered. Please use a different email.","error")
        return redirect(url_for('main.settings'))

    old_email = user.email
    user.email = new_email
    db.session.commit()

    # Log the change
    activity = UserActivity(user_id=user.id, activity_type="email_change", old_value=old_email, new_value=new_email)
    db.session.add(activity)
    db.session.commit()

    session.clear()
    flash("Email updated successfully. Please log in with your new email.","caution")
    return redirect(url_for('main.login'))

@main.route('/update_password', methods=['POST'])
def update_password():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your password.","error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))
    current_password = request.form.get('current_password').strip()
    new_password     = request.form.get('new_password').strip()
    confirm_password = request.form.get('confirm_password').strip()
    if not user.check_password(current_password):
        flash("Incorrect current password. Please try again.", "error")
        return redirect(url_for('main.settings'))
    if new_password != confirm_password:
        flash("New passwords do not match. Please try again.", "error")
        return redirect(url_for('main.settings'))
    user.set_password(new_password)
    db.session.commit()
    session.clear()
    flash("Password updated successfully. Please log in with your new credentials.", "caution")
    return redirect(url_for('main.login'))
@main.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to delete your account.","error")
        return redirect(url_for('main.login'))
    user = User.query.get(user_id)
    if not user:
        flash("User not found.","error")
        return redirect(url_for('main.login'))
    delete_password = request.form.get('delete_password').strip()
    if not user.check_password(delete_password):
        flash("Incorrect password. Please try again.", "error")
        return redirect(url_for('main.settings'))
    MediaEntry.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Your account has been permanently deleted.", "caution")
    return redirect(url_for('main.welcome'))
@main.route('/foryou')
def for_you():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to access this page.", "error")
        return redirect(url_for('main.login'))

    # Fetch the current user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))

    # Fetch the user's friends
    friends = user.friends

    # Media data
    books = Book.query.filter_by(user_id=user_id).all()
    movies = Movie.query.filter_by(user_id=user_id).all()
    tv_shows = TVShow.query.filter_by(user_id=user_id).all()
    music = Music.query.filter_by(user_id=user_id).all()

    raw_media_counts = {
        "book": len(books),
        "movie": len(movies),
        "tv_show": len(tv_shows),
        "music": len(music),
    }

    display_media_counts = {
        "Books": raw_media_counts["book"],
        "Movies": raw_media_counts["movie"],
        "TV Shows": raw_media_counts["tv_show"],
        "Music": raw_media_counts["music"],
    }

    # Add genre breakdowns
    def get_genre_counts(queryset):
        counts = {}
        for entry in queryset:
            if entry.genre:
                counts[entry.genre] = counts.get(entry.genre, 0) + 1
        return counts

    genre_breakdowns = {
        "Books": get_genre_counts(books),
        "Movies": get_genre_counts(movies),
        "TV Shows": get_genre_counts(tv_shows),
        "Music": get_genre_counts(music),
    }

    # Generate the identity label
    identity_label = get_user_media_identity(raw_media_counts)

    # ✅ Pass the required variables to the template
    return render_template(
        "foryou.html",
        identity=identity_label,
        username=user.name,
        media_counts=display_media_counts,
        genre_breakdowns=genre_breakdowns,
        friends=friends
    )



@main.route('/notifications')
def notifications():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to view notifications.", "error")
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for('main.login'))

    # Retrieve pending friend requests
    friend_requests = FriendRequest.query.filter_by(receiver_id=user.id, status="pending").all()

    # Retrieve activity updates from friends
    friend_ids = [f.id for f in user.friends]
    activities = UserActivity.query.filter(
        UserActivity.user_id.in_(friend_ids)
    ).order_by(UserActivity.timestamp.desc()).all()

    # Retrieve media snapshots and parse the JSON data for template use
    snapshots = MediaSnapshot.query.filter_by(receiver_id=user.id).all()
    for snapshot in snapshots:
        try:
            snapshot.parsed_data = json.loads(snapshot.snapshot_data)
        except json.JSONDecodeError:
            snapshot.parsed_data = {"error": "Invalid snapshot data"}

    # Retrieve all friend shares without a limit
    friend_entries = (
        MediaEntry.query
        .filter_by(user_id=user.id)
        .filter(MediaEntry.title.contains('(shared)'))
        .order_by(MediaEntry.id.desc())
        .all()
    )

    # Add the friend’s name who shared it
    real_friends = []
    for entry in friend_entries:
        clean = entry.title.rsplit(' (shared)', 1)[0]
        sharer = (
            MediaEntry.query
            .filter(
                MediaEntry.user_id.in_(friend_ids),
                MediaEntry.media_type == entry.media_type,
                MediaEntry.title == clean
            )
            .order_by(MediaEntry.id.desc())
            .first()
        )
        if sharer:
            entry.sharer_name = sharer.user.name
            real_friends.append(entry)

    return render_template(
        'notifications.html',
        user=user,
        friend_requests=friend_requests,
        activities=activities,
        snapshots=snapshots,
        friend_entries=real_friends  # Now this includes all shares
    )


@main.route('/respond_friend_request/<int:request_id>/<action>', methods=['POST'])
def respond_friend_request(request_id, action):
    user = User.query.get(session.get('user_id'))
    friend_request = FriendRequest.query.get(request_id)

    if not user or not friend_request or friend_request.receiver_id != user.id:
        flash("Invalid request.", "error")
        return redirect(url_for('main.notifications'))

    if action == "accept":
        # Establish the friendship
        sender = friend_request.sender
        receiver = friend_request.receiver
        sender.friends.append(receiver)
        receiver.friends.append(sender)
        friend_request.status = "accepted"
        flash(f"You are now friends with {sender.name}!", "success")
    elif action == "reject":
        friend_request.status = "rejected"
        flash("Friend request rejected.", "caution")
    else:
        flash("Invalid action.", "error")

    db.session.commit()
    return redirect(url_for('main.notifications'))

@main.route('/accept_friend_request/<int:request_id>', methods=['POST'])
def accept_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request:
        sender = friend_request.sender
        receiver = friend_request.receiver

        # Make them friends
        sender.friends.append(receiver)
        receiver.friends.append(sender)

        # Remove the request
        db.session.delete(friend_request)
        db.session.commit()

        flash(f"You are now friends with {sender.name}!", "success")
    else:
        flash("Friend request not found.", "error")
    
    return redirect(url_for('main.notifications'))

@main.route('/reject_friend_request/<int:request_id>', methods=['POST'])
def reject_friend_request(request_id):
    friend_request = FriendRequest.query.get(request_id)
    if friend_request:
        db.session.delete(friend_request)
        db.session.commit()
        flash("Friend request rejected.", "caution")
    else:
        flash("Friend request not found.", "error")
    
    return redirect(url_for('main.notifications'))

@main.app_context_processor
def inject_unread_notifications():
    user_id = session.get('user_id')
    if user_id:
        # Count unseen snapshots, friend requests, and activities
        snapshot_unread = MediaSnapshot.query.filter_by(receiver_id=user_id, seen=False).count()
        activity_unread = UserActivity.query.filter(
            UserActivity.user_id != user_id,
            UserActivity.seen == False
        ).count()
        unread_requests = FriendRequest.query.filter_by(receiver_id=user_id, status="pending", seen=False).count()
        
        return dict(unread_notifications=snapshot_unread + activity_unread + unread_requests)
    
    return dict(unread_notifications=0)


@main.route('/send_snapshot', methods=['POST'])
def send_snapshot():
    user = User.query.get(session.get('user_id'))
    if not user:
        return jsonify({"success": False, "message": "Please log in to share your media snapshot."})

    receiver_id = request.form.get('receiver_id', type=int)
    receiver = User.query.get(receiver_id)
    if not receiver or receiver == user or receiver not in user.friends:
        return jsonify({"success": False, "message": "Invalid receiver."})

    # Check if the file part is present
    if 'snapshot' not in request.files:
        return jsonify({"success": False, "message": "No snapshot file found."})

    file = request.files['snapshot']
    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type. Please upload a PNG, JPG, JPEG, or GIF file."})

    # Generate a unique filename to prevent collisions
    filename = f"{uuid.uuid4().hex}.png"
    upload_folder = os.path.join(current_app.static_folder, 'snapshots')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    # Save the snapshot entry in the database
    snapshot = MediaSnapshot(
        sender_id=user.id,
        receiver_id=receiver.id,
        snapshot_data=filename  # Store just the filename
    )
    db.session.add(snapshot)
    db.session.commit()

    return jsonify({"success": True, "message": "Snapshot sent successfully!"})

@main.route('/mark_all_notifications_read', methods=['POST'])
def mark_all_notifications_read():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Please log in to mark all notifications as read."})

    # Mark all friend requests as seen
    FriendRequest.query.filter_by(receiver_id=user_id, status="pending").update({"seen": True})
    
    # Mark all activities as seen
    UserActivity.query.filter_by(user_id=user_id, seen=False).update({"seen": True})
    
    # Mark all snapshots as seen
    MediaSnapshot.query.filter_by(receiver_id=user_id, seen=False).update({"seen": True})
    
    db.session.commit()

    return jsonify({"success": True, "message": "All notifications marked as read."})

