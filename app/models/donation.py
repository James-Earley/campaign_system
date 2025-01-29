def create_donation_model(db):
    class Donation(db.Model):
        __tablename__ = 'donations'
        __table_args__ = {'extend_existing': True}  # Ensure table can be redefined without error

        id = db.Column(db.Integer, primary_key=True)
        citizen_id = db.Column(db.Integer, db.ForeignKey('citizens.id'), nullable=False)
        campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        donation_date = db.Column(db.DateTime, server_default=db.func.now())

        # Relationships
        citizen = db.relationship('Citizen', backref='donation_details', lazy='joined')
        campaign = db.relationship('Campaign', backref='donation_details', lazy='joined')

    return Donation
