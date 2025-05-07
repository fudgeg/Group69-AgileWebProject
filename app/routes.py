from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import db, MediaEntry, User
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def welcome():
    return render_template('welcome.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not first_name or not last_name or not email or not password:
            flash("All fields are required")
            return redirect(url_for('main.signup'))

        name = f"{first_name} {last_name}"

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in')
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
    flash('You have been logged out')
    return redirect(url_for('main.welcome'))




@main.route('/home')
def home():
    user_id = session.get('user_id')
    print(f"[DEBUG] Session user_id: {user_id}")

    if not user_id:
        flash("You must be logged in to view this page.")
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    print(f"[DEBUG] User from DB: {user}")

    if not user:
        flash("User not found.")
        return redirect(url_for('main.login'))

    # Query the most recent media entries (e.g., last 5)
    recent_entries = MediaEntry.query.order_by(MediaEntry.id.desc()).limit(5).all()

    # ✅ Get media entries created by the user's friends (limit for performance)
    friend_ids = [f.id for f in user.friends]
    friend_entries = (
        MediaEntry.query
        .filter(MediaEntry.user_id.in_(friend_ids))
        .order_by(MediaEntry.id.desc())
        .limit(5)
        .all()
    )

    return render_template('home.html', user=user, recent_entries=recent_entries, friend_entries=friend_entries)



@main.route('/friends', methods=['GET', 'POST'])
def friends():
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("Please log in to view friends.")
        return redirect(url_for('main.login'))

    # All users except the current user and existing friends
    recommended = User.query.filter(
        User.id != user.id,
        ~User.id.in_([f.id for f in user.friends])
    ).all()

    return render_template('friends.html', user=user, friends=user.friends, recommended=recommended)


@main.route('/add_friend/<int:friend_id>', methods=['POST'])
def add_friend(friend_id):
    user = User.query.get(session.get('user_id'))
    friend = User.query.get(friend_id)

    if not user or not friend or friend == user:
        flash("Invalid request.")
        return redirect(url_for('main.friends'))

    if friend in user.friends:
        flash("You're already friends.")
        return redirect(url_for('main.friends'))

    user.friends.append(friend)
    friend.friends.append(user)
    db.session.commit()

    flash(f"You are now friends with {friend.name}!")
    return redirect(url_for('main.friends'))


@main.route('/upload', methods=['GET', 'POST'])
def upload_page():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to upload media.")
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        media_type = request.form.get('mediaType')
        title = request.form.get('mediaTitle')
        if media_type and title:
            new_entry = MediaEntry(media_type=media_type, title=title, user_id=user_id)
            db.session.add(new_entry)
            db.session.commit()
            flash("Media entry added.")

        return redirect(url_for('main.upload_page'))

    # Show only the entries for the logged-in user only by filtering by user_id
    entries = MediaEntry.query.filter_by(user_id=user_id).all()
    return render_template('upload.html', entries=entries)

@main.route('/settings')
def settings():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to access settings.")
        return redirect(url_for('main.login'))
    
    # Get the current user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
        return redirect(url_for('main.login'))

    # Pass the user to the template
    return render_template('settings.html', user=user)


@main.route('/update_username', methods=['POST'])
def update_username():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your username.")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
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
        flash("Username cannot be empty.")
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
        flash("You must be logged in to update your email.")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
        return redirect(url_for('main.login'))

    # Get the new email and password from the form
    new_email = request.form.get('email').strip().lower()
    password = request.form.get('password').strip()
    
    # Verify password
    if not user.check_password(password):
        flash("Incorrect password. Please try again.")
        return redirect(url_for('main.settings'))
    
    # Check if the new email is valid
    if not new_email:
        flash("Email cannot be empty.")
        return redirect(url_for('main.settings'))
    
    # Check if the new email is already taken
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user:
        flash("This email is already registered. Please use a different email.")
        return redirect(url_for('main.settings'))
    
    # Update the email
    user.email = new_email
    db.session.commit()
    
    # Log the user out to force re-login with the new email
    session.clear()
    flash("Email updated successfully. Please log in with your new email.")
    return redirect(url_for('main.login'))




@main.route('/foryou')
def for_you():
    return render_template('foryou.html')

@main.route('/update_password', methods=['POST'])
def update_password():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your password.")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
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
    
    # Provide user feedback
    flash("Password updated successfully.", "success")
    return redirect(url_for('main.settings'))


@main.route('/delete_account', methods=['POST'])
def delete_account():
    # Check if the user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to delete your account.")
        return redirect(url_for('main.login'))
    
    # Get the logged-in user
    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
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
    flash("Your account has been permanently deleted.", "error")
    return redirect(url_for('main.welcome'))
