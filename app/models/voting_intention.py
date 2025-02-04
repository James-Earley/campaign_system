# app/models/voting_intention.py

from datetime import datetime

_model = None  # Added singleton pattern

def create_voting_intention_model(db, models=None):
    """Creates the VotingIntention model with singleton pattern."""
    global _model

    if _model is not None:
        return "VotingIntention", _model  # ✅ Fix: Return a tuple (model name, model class)

    class VotingIntention(db.Model):
        __tablename__ = 'voting_intentions'
        __table_args__ = {'extend_existing': True}
       
        id = db.Column(db.Integer, primary_key=True)
        voter_id = db.Column(db.Integer, db.ForeignKey('voters.id'), nullable=False)
        change_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
        new_intention = db.Column(db.String(50), nullable=False)

        voter = db.relationship('Voter', backref=db.backref('voting_intentions', lazy='dynamic'))

        def __repr__(self):
            return f'<VotingIntention {self.voter_id}: {self.new_intention}>'

    _model = VotingIntention
    return "VotingIntention", _model  # ✅ Fix: Return a tuple (model name, model class)
