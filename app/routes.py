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
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for('main.signup'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.')
            return redirect(url_for('main.login'))

        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print(f"[SIGNUP] New user created: {user.name} | {user.email}")
        flash('Signup successful. Please log in.')
        return redirect(url_for('main.login'))

    return render_template('signup.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for('main.login'))

        user = User.query.filter_by(email=email).first()
        if user:
            print(f"[LOGIN ATTEMPT] Found user: {user.email}")
        else:
            print(f"[LOGIN ATTEMPT] No user found with email: {email}")

        if user and user.check_password(password):
            session['user_id'] = user.id
            print(f"[LOGIN SUCCESS] Logged in user: {user.name} ({user.email})")
            flash('Logged in successfully.')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.')

    return render_template('login.html')


@main.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    print(f"[LOGOUT] User ID {user_id} logged out.")
    flash('You have been logged out.')
    return redirect(url_for('main.login'))


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

    return render_template('home.html', user=user)



@main.route('/friends')
def friends():
    return render_template('friends.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload_page():
    if request.method == 'POST':
        media_type = request.form.get('mediaType')
        title = request.form.get('mediaTitle')
        if media_type and title:
            new_entry = MediaEntry(media_type=media_type, title=title)
            db.session.add(new_entry)
            db.session.commit()
        return redirect(url_for('main.upload_page'))

    entries = MediaEntry.query.all()
    return render_template('upload.html', entries=entries)

@main.route('/settings')
def settings():
    return render_template('settings.html')

@main.route('/foryou')
def for_you():
    return render_template('foryou.html')
