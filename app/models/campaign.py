from datetime import datetime

def create_campaign_model(db, models):
    """Creates the Campaign model."""

    # Ensure required models exist
    if "CampaignTeam" not in models:
        raise KeyError("CampaignTeam model must be initialized before Campaign.")

    if "volunteer_assignments" not in models:  
        raise KeyError("volunteer_assignments table must be initialized before Campaign.")

    # Ensure CampaignEvent exists
    CampaignEvent = models.get("CampaignEvent", None)  

    class Campaign(db.Model):
        __tablename__ = 'campaigns'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=True)
        start_date = db.Column(db.DateTime, default=datetime.utcnow)
        end_date = db.Column(db.DateTime, nullable=True)
        status = db.Column(db.String(50), default='planned')

        campaign_teams = db.relationship("CampaignTeam", back_populates="campaign", cascade="all, delete-orphan")

        # ✅ Ensure the relationship is always set
        events = db.relationship("CampaignEvent", back_populates="campaign", cascade="all, delete-orphan")

        volunteers = db.relationship(
            "Volunteer",
            secondary="volunteer_assignments",
            back_populates="campaigns"
        )

        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        def __repr__(self):
            return f'<Campaign {self.name}>'

    return "Campaign", Campaign  # ✅ Ensure correct tuple return
