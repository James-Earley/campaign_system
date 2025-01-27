from flask import Flask
from app.models import db  # our SQLAlchemy instance

def create_app():
    app = Flask(__name__)
    
    # Load configuration from the Config class in settings.py
    app.config.from_object('app.settings.MySettings')

    # Initialise the database with our app
    db.init_app(app)

    # Automatically create tables if not yet present
    with app.app_context():
        db.create_all()

    # Register your main blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app
