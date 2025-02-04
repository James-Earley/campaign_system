from datetime import datetime

_model = None

def create_event_model(db, models=None):
    """Creates the Event model with proper relationships."""
    global _model
    
    if _model is not None:
        return "Event", _model  # ✅ Fix: Return a tuple (model name, model class)

    class Event(db.Model):
        __tablename__ = 'events'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False) 
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.DateTime, nullable=False)
        location = db.Column(db.String(255), nullable=False)
        event_type = db.Column(db.String(50))
        capacity = db.Column(db.Integer)
        
        # ✅ Fix: Prevent relationship conflicts with 'overlaps'
        staffers = db.relationship(
            'EventStaffer', 
            back_populates='event', 
            lazy='dynamic', 
            cascade="all, delete-orphan",
            overlaps="event_staffing, staff_assignments"
        )

        volunteer_assignments = db.relationship(
            'VolunteerAssignment', 
            back_populates='event', 
            lazy='dynamic'
        )

        def __repr__(self):
            return f'<Event {self.name}>'

    _model = Event
    return "Event", _model  # ✅ Fix: Return a tuple (model name, model class)
