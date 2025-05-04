from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def welcome():
    return render_template('welcome.html')

@main.route('/login')
def login():
    return render_template('login.html')

@main.route('/signup')
def signup():
    return render_template('signup.html')

@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/friends')
def friends():
    return render_template('friends.html')

@main.route('/import')
def import_page():
    return render_template('import.html')

@main.route('/settings')
def settings():
    return render_template('settings.html')

@main.route('/foryou')
def for_you():
    return render_template('foryou.html')
