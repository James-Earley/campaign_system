def create_campaign_model(db):
    class Campaign(db.Model):
        __tablename__ = 'campaigns'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        description = db.Column(db.Text, nullable=True)
        start_date = db.Column(db.Date, nullable=False)
        end_date = db.Column(db.Date, nullable=False)
        created_at = db.Column(db.DateTime, server_default=db.func.now())

    return Campaign