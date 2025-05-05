from flask import Flask
from .routes import main
from .models import db  # Add this line

def create_app():
    app = Flask(__name__)
    
    # SQLAlchemy config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soulmaps.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # Initialize the database with the app

    app.register_blueprint(main)
    return app
