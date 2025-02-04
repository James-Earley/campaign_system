from datetime import datetime

_model = None  # Added singleton pattern

def create_contact_model(db, models=None):
    """Creates the Contact model with singleton pattern."""
    global _model
    
    if _model is not None:
        return "Contact", _model  # ✅ Fix: Return a tuple (model name, model class)

    class Contact(db.Model):
        __tablename__ = 'contacts'
        __table_args__ = {'extend_existing': True}  # ✅ Ensure it allows updates to schema

        id = db.Column(db.Integer, primary_key=True)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
        contact_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        outcome = db.Column(db.String(255), nullable=False)
        follow_up_required = db.Column(db.Boolean, default=False)
        contact_method = db.Column(db.String(50), nullable=False)

        citizen = db.relationship('Citizen', backref=db.backref('contacts', lazy=True))

        def __repr__(self):
            return f'<Contact {self.id} with Citizen {self.citizen_id}>'

    _model = Contact
    return "Contact", _model  # ✅ Fix: Return a tuple (model name, model class)
