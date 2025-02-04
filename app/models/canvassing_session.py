# app/models/canvassing_session.py
from datetime import datetime
from .enums import TaskStatus

def create_canvassing_session_model(db, models=None):
    """Creates the CanvassingSession model.
    
    Args:
        db: SQLAlchemy instance
        models: Optional dict of other initialized models
    """
    class CanvassingSession(db.Model):
        __tablename__ = 'canvassing_sessions'
        __table_args__ = (
            db.ForeignKeyConstraint(
                ['campaign_id'], ['campaigns.id'],
                name='fk_canvassing_campaign'
            ),
            db.ForeignKeyConstraint(
                ['assigned_staff'], ['campaign_teams.id'],
                name='fk_canvassing_staff'
            ),
            {'extend_existing': True}
        )

        id = db.Column(db.Integer, primary_key=True)
        campaign_id = db.Column(db.Integer, nullable=False)
        assigned_staff = db.Column(db.Integer, nullable=False)
        area_code = db.Column(db.String(10))
        target_completion_date = db.Column(db.DateTime)
        task_status = db.Column(
            db.Enum(TaskStatus),
            default=TaskStatus.PENDING,
            nullable=False
        )
        notes = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # Add relationships
        assigned_team = db.relationship(
            "CampaignTeam",
            foreign_keys=[assigned_staff],
            backref=db.backref("canvassing_sessions", lazy="dynamic")
        )

        campaign = db.relationship(
            "Campaign",
            foreign_keys=[campaign_id],
            backref=db.backref("canvassing_sessions", lazy="dynamic")
        )

        def __repr__(self):
            return f'<CanvassingSession {self.id} - {self.task_status.value}>'

    return "CanvassingSession", CanvassingSession  # ✅ Fix: Return a tuple (model name, model class)
