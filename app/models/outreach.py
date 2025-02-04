from datetime import datetime

_model = None

def create_outreach_model(db, models=None):
    """Creates the Outreach model with singleton pattern."""
    global _model
    
    if _model is not None:
        return "Outreach", _model  # ✅ Fix: Return a tuple (model name, model class)

    class Outreach(db.Model):
        __tablename__ = 'outreach'
        # Proper way to define table arguments
        __table_args__ = (
            db.UniqueConstraint('team_id', 'citizen_id', 'contact_date', 
                              name='uix_outreach_team_citizen_date'),
            {'extend_existing': True}
        )

        id = db.Column(db.Integer, primary_key=True)  # Fixed QZInteger to Integer
        team_id = db.Column(db.Integer, db.ForeignKey('campaign_teams.id'), nullable=False)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
        outreach_type = db.Column(db.String(50), nullable=False)
        status = db.Column(db.String(20), default='pending')
        contact_date = db.Column(db.DateTime)
        response = db.Column(db.String(50))
        follow_up_needed = db.Column(db.Boolean, default=False)
        follow_up_date = db.Column(db.DateTime)
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Relationships
        team = db.relationship(
            'CampaignTeam',
            backref=db.backref('outreach_activities', lazy='dynamic', cascade='all, delete-orphan')
        )
        citizen = db.relationship(
            'Citizen',
            backref=db.backref('outreach_contacts', lazy='dynamic', cascade='all, delete-orphan')
        )

        def __repr__(self):
            return f'<Outreach {self.outreach_type} to Citizen {self.citizen_id}>'

    _model = Outreach
    return "Outreach", _model  # ✅ Fix: Return a tuple (model name, model class)
