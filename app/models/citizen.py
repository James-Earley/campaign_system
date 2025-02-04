from datetime import datetime

def create_citizen_model(db, models):
    """Creates the Citizen model."""
    
    class Citizen(db.Model):
        __tablename__ = 'citizens'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        phone = db.Column(db.String(20))
        address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)
        constituency = db.Column(db.String(100), nullable=False)
        registration_status = db.Column(db.String(50), default='unregistered')
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        address = db.relationship('Address', backref=db.backref('citizens', lazy=True))
        donations = db.relationship("Donation", back_populates="citizen")

        def __repr__(self):
            return f'<Citizen {self.name}>'
    
    models["Citizen"] = Citizen  
    return "Citizen", Citizen  # ✅ Fix: Return a tuple (model name, model class)
