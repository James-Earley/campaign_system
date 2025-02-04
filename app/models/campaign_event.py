from datetime import datetime

def create_campaign_event_model(db, models):  
    """Creates the CampaignEvent model."""

    class CampaignEvent(db.Model):
        __tablename__ = 'campaign_events'
        __table_args__ = (
            db.ForeignKeyConstraint(
                ['campaign_id'], ['campaigns.id'],
                name='fk_event_campaign'
            ),
            {'extend_existing': True}
        )

        id = db.Column(db.Integer, primary_key=True)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        date = db.Column(db.DateTime, nullable=False)
        location = db.Column(db.String(255), nullable=False)
        event_type = db.Column(db.String(50))
        capacity = db.Column(db.Integer)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # ✅ Relationship with Campaign model (Ensure correct back_populates)
        campaign = db.relationship("Campaign", back_populates="events")

        def __repr__(self):
            return f'<CampaignEvent {self.name}>'

    return "CampaignEvent", CampaignEvent  # ✅ Ensure function returns a tuple
