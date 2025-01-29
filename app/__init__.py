from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

# Define base_dir to fix NameError
base_dir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__)
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "instance", "campaign.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Initialize models inside the app context
    with app.app_context():
        from app.models import initialize_models
        Campaign, Citizen, Donation = initialize_models(db)

    # Register blueprints
    from app.routes import citizens_bp, campaigns_bp, main_bp
    app.register_blueprint(citizens_bp, url_prefix='/api/v1/citizens')
    app.register_blueprint(campaigns_bp, url_prefix='/api/v1/campaigns')
    app.register_blueprint(main_bp)

    return app
