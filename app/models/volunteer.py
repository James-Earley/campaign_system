from datetime import datetime

def create_volunteer_model(db, models):
    """Creates the Volunteer model."""

    # ✅ Retrieve Many-to-Many association table
    volunteer_assignments = models.get("volunteer_assignments", None)

    if "volunteer_assignments" not in models:  
        raise KeyError("volunteer_assignments table must be initialized before Volunteer.")

    class Volunteer(db.Model):
        __tablename__ = 'volunteers'
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)
        first_name = db.Column(db.String(100), nullable=False)
        last_name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        phone = db.Column(db.String(20))
        address = db.Column(db.String(255))
        city = db.Column(db.String(100))
        state = db.Column(db.String(2))
        zip_code = db.Column(db.String(10))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

        # ✅ Many-to-Many relationship with Campaigns
        campaigns = db.relationship(
            "Campaign",
            secondary="volunteer_assignments",  # Use string reference
            back_populates="volunteers"
        )

        assignments = db.relationship("VolunteerAssignment", back_populates="volunteer")

        def __repr__(self):
            return f'<Volunteer {self.first_name} {self.last_name}>'

    # ✅ Fix: Return a tuple (model name, model class)
    return "Volunteer", Volunteer
