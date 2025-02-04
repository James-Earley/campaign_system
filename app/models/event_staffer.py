from datetime import datetime
from .enums import EventStatus

_model = None

def create_event_staffer_model(db, models=None):
    """Creates the EventStaffer model with enhanced role tracking."""
    global _model

    if _model is not None:
        return "EventStaffer", _model  # ✅ Fix: Return a tuple (model name, model class)

    class EventStaffer(db.Model):
        __tablename__ = 'event_staffers'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
        volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteers.id'), nullable=False)
        role = db.Column(db.String(50), nullable=False)  # e.g., 'coordinator', 'security', 'registration'
        shift_start = db.Column(db.DateTime, nullable=False)
        shift_end = db.Column(db.DateTime, nullable=False)
        status = db.Column(db.String(20), default='scheduled')  # e.g., 'scheduled', 'checked-in', 'completed'
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        status = db.Column(
            db.Enum(EventStatus),
            default=EventStatus.SCHEDULED,
            nullable=False
        )

        # ✅ Fix: Prevent relationship conflicts with 'overlaps'
        event = db.relationship(
            'Event', 
            back_populates='staffers', 
            overlaps="event_staffing, staff_assignments"
        )

        volunteer = db.relationship('Volunteer', backref=db.backref(
            'event_assignments',
            lazy='dynamic',
            cascade='all, delete-orphan'
        ))

        def __repr__(self):
            return f'<EventStaffer {self.volunteer_id} for Event {self.event_id}>'

        @property
        def is_current(self):
            """Check if the shift is currently active."""
            now = datetime.utcnow()
            return self.shift_start <= now <= self.shift_end

    _model = EventStaffer
    return "EventStaffer", _model  # ✅ Fix: Return a tuple (model name, model class)
