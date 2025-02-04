from datetime import datetime

def create_campaign_team_model(db, models):
    """Creates the CampaignTeam model (Ensures Singleton)."""

    if "CampaignTeam" in models:  # ✅ Ensure it's not redefined
        return "CampaignTeam", models["CampaignTeam"]  # ✅ Fix: Return a tuple

    class CampaignTeam(db.Model):
        __tablename__ = 'campaign_teams'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text)
        contact_email = db.Column(db.String(100))
        contact_phone = db.Column(db.String(20))
        team_size = db.Column(db.Integer)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        #  Ensure the back_populates reference is correct
        campaign = db.relationship("Campaign", back_populates="campaign_teams")

        def __repr__(self):
            return f'<CampaignTeam {self.name}>'

    models["CampaignTeam"] = CampaignTeam  # ✅ Store it in models to prevent duplicates
    return "CampaignTeam", CampaignTeam  # ✅ Fix: Return a tuple (model name, model class)
