from flask import Flask
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .models import db, User    # ✅ Import db & User from models
from .config import Config       # ─── pull in our Config class

def create_app():
    app = Flask(__name__)

    # load all config from environment via Config 
    app.config.from_object(Config)

    # initialize database
    db.init_app(app)
    CSRFProtect(app)  # Enables CSRF globally
    Migrate(app, db)
     
    # register your main blueprint
    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        if not User.query.filter_by(email='admin@example.com').first():
            default_user = User(
                name='Admin',
                email='admin@example.com'
            )
            default_user.set_password('password123')
            db.session.add(default_user)
            db.session.commit()
            print("[DB] Default user created: admin@example.com / password123")

    return app