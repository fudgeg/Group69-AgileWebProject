from flask import Flask
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from .models import db, User    
from .config import Config      

# create_app function initializes the Flask application
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


    return app