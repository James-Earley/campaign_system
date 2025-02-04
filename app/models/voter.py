from flask_sqlalchemy import SQLAlchemy

_model = None

def create_voter_model(db, models=None):
    """Creates the Voter model with singleton pattern."""
    global _model
    
    if _model is not None:
        return "Voter", _model  # ✅ Fix: Return a tuple (model name, model class)

    class Voter(db.Model):
        __tablename__ = 'voters'
        __table_args__ = {'extend_existing': True}
       
        id = db.Column(db.Integer, primary_key=True)  # Changed from voter_id
        registration_date = db.Column(db.DateTime, nullable=False)
        last_known_vote_intention = db.Column(db.String(50), nullable=True)
        last_intention_change_date = db.Column(db.DateTime, nullable=True)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
       
        citizen = db.relationship('Citizen', backref=db.backref('voter', uselist=False, lazy=True))

        def __repr__(self):
            return f'<Voter {self.id} for Citizen {self.citizen_id}>'

    _model = Voter
    return "Voter", _model  # ✅ Fix: Return a tuple (model name, model class)
