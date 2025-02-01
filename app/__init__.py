from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set up database
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "instance", "campaign.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize database
    db.init_app(app)

    # Ensure instance directory exists
    os.makedirs(os.path.join(base_dir, "instance"), exist_ok=True)

    # Import models AFTER initializing db (avoids circular import)
    with app.app_context():
        from app.models import initialize_models
        Campaign, Citizen, Donation = initialize_models(db)
        
        # ✅ Ensure tables are created
        db.create_all()

    # Register blueprints AFTER app context setup
    from app.routes import citizens_bp, campaigns_bp, donations_bp ,main_bp
    app.register_blueprint(citizens_bp, url_prefix='/api/v1/citizens')
    app.register_blueprint(campaigns_bp, url_prefix='/api/v1/campaigns')
    app.register_blueprint(donations_bp, url_prefix='/api/v1/donations')  
    app.register_blueprint(main_bp, url_prefix='/')

    return app

app = create_app()
