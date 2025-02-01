from flask_sqlalchemy import SQLAlchemy

def create_citizen_model(db):
    """Creates the Citizen model dynamically but ensures it is only created once."""

    # Check if the table is already registered
    if 'citizens' in db.metadata.tables:
        return db.Model._decl_class_registry.get('citizens', None)  #  Corrected lookup

    class Citizen(db.Model):
        __tablename__ = 'citizens'
        __table_args__ = {'extend_existing': True}  #  Prevent redefinition error

        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        constituency = db.Column(db.String(100), nullable=False)

    return Citizen
