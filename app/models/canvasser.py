from datetime import datetime

_model = None

def create_canvasser_model(db, models=None):
    """Creates the Canvasser model with proper foreign key relationships."""
    global _model

    if _model is not None:
        return "Canvasser", _model  # ✅ Fix: Return a tuple (model name, model class)

    class Canvasser(db.Model):
        __tablename__ = 'canvassers'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)  # Changed from voter_id
        previous_intention = db.Column(db.String(50))
        current_intention = db.Column(db.String(50))
        last_contact_date = db.Column(db.DateTime)
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Define relationship to Citizen model instead of Voter
        citizen = db.relationship('Citizen', backref=db.backref('canvasser_info', lazy=True))

        def __repr__(self):
            return f'<Canvasser {self.id} for Citizen {self.citizen_id}>'

    _model = Canvasser
    return "Canvasser", _model  # ✅ Fix: Return a tuple (model name, model class)
