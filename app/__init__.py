from flask import Flask
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .models import db, User  

def create_app():
    app = Flask(__name__)
    app.secret_key = 'super_secret_key_123'

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soulmaps.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  
    CSRFProtect(app)  # Enables CSRF globally
    Migrate(app, db)
     
    from .routes import main
    app.register_blueprint(main)

    #  create default data
    with app.app_context():
        if not User.query.filter_by(email='admin@example.com').first():
            default_user = User(name='Admin', email='admin@example.com')
            default_user.set_password('password123')
            db.session.add(default_user)
            db.session.commit()
            print("[DB] Default user created: admin@example.com / password123")

    return app
