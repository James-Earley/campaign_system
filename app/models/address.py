from datetime import datetime
import logging

logger = logging.getLogger(__name__)

_model = None

def create_address_model(db, models=None):
    """Creates the Address model."""
    global _model
    
    if _model is not None:
        logger.info("Address model already initialized. Returning existing model.")
        return "Address", _model  # ✅ Fix: Return a tuple instead of just the model

    logger.info("Initializing Address model...")

    class Address(db.Model):
        __tablename__ = 'addresses'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        street = db.Column(db.String(255), nullable=False)
        city = db.Column(db.String(100), nullable=False)
        state = db.Column(db.String(2), nullable=False)
        zip_code = db.Column(db.String(10), nullable=False)
        created_at = db.Column(db.DateTime, default=db.func.now())
        updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

        def __repr__(self):
            return f'<Address {self.street}, {self.city}>'

    _model = Address
    logger.info("Successfully initialized Address model.")
    return "Address", _model  # ✅ Fix: Return a tuple (model name, model class)
