from flask_sqlalchemy import SQLAlchemy

def create_volunteer_assignment_model(db, models):  # ✅ FIX: Ensure models parameter is included
    """Creates the VolunteerAssignment model and the many-to-many association table."""

    # ✅ Ensure association table is stored in models
    if "VolunteerAssignment" in models:
        return "VolunteerAssignment", models["VolunteerAssignment"]  # ✅ FIX: Return tuple

    # ✅ Many-to-Many Association Table
    volunteer_assignments = db.Table(
        "volunteer_assignments",
        db.metadata,
        db.Column("volunteer_id", db.Integer, db.ForeignKey("volunteers.id", ondelete="CASCADE"), primary_key=True),
        db.Column("campaign_id", db.Integer, db.ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True),
        extend_existing=True  # ✅ Prevents duplicate table errors
    )

    # ✅ Individual Assignment Model
    class VolunteerAssignment(db.Model):
        __tablename__ = "volunteer_assignment"
        __table_args__ = {'extend_existing': True}

        id = db.Column(db.Integer, primary_key=True)  # ✅ Fix: Use `id` as the primary key
        volunteer_id = db.Column(db.Integer, db.ForeignKey("volunteers.id"), nullable=False)
        campaign_event_id = db.Column(db.Integer, db.ForeignKey("campaign_events.id"), nullable=True)
        canvassing_session_id = db.Column(db.Integer, db.ForeignKey("canvassing_sessions.id"), nullable=True)
        event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)

        task = db.Column(db.String(255), nullable=False)
        assigned_at = db.Column(db.DateTime, default=db.func.now())
        created_at = db.Column(db.DateTime, default=db.func.now())
        updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

        # Relationships
        volunteer = db.relationship("Volunteer", back_populates="assignments")

        campaign_event = db.relationship(
            "CampaignEvent",
            backref=db.backref("volunteer_assignments", lazy="dynamic"),
            foreign_keys=[campaign_event_id]
        )

        canvassing_session = db.relationship(
            "CanvassingSession",
            backref=db.backref("volunteer_assignments", lazy="dynamic"),
            foreign_keys=[canvassing_session_id]
        )

        event = db.relationship(
            "Event",
            back_populates="volunteer_assignments"
        )

        def __repr__(self):
            return f"<VolunteerAssignment {self.volunteer_id}: {self.task}>"

    # ✅ Store the model in `models`
    models["VolunteerAssignment"] = VolunteerAssignment
    models["volunteer_assignments"] = volunteer_assignments  # ✅ Also store the association table
    return "VolunteerAssignment", VolunteerAssignment  # ✅ FIX: Return a tuple (model name, model class)
