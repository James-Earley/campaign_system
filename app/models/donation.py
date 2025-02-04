# app/models/donation.py
from datetime import datetime
from .enums import DonationStatus

def create_donation_model(db, models=None):
    """Creates the Donation model.
    
    Args:
        db: SQLAlchemy instance
        models: Optional dict of other initialized models
    """
    
    class Donation(db.Model):
        __tablename__ = 'donations'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
        amount = db.Column(db.Numeric(10, 2), nullable=False)
        payment_method = db.Column(db.String(50))
        donation_type = db.Column(db.String(50))
        donation_date = db.Column(db.DateTime, default=datetime.utcnow)
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Fixed duplicate status column
        status = db.Column(
            db.Enum(DonationStatus),
            default=DonationStatus.PENDING,
            nullable=False
        )

        # Relationships
        citizen = db.relationship("Citizen", back_populates="donations") 
        campaign = db.relationship('Campaign', backref=db.backref('donations', lazy='dynamic'))

        def __repr__(self):
            return f'<Donation ${self.amount} by Citizen {self.citizen_id}>'

    return "Donation", Donation  # ✅ Fix: Return a tuple (model name, model class)
