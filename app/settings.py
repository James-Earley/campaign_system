import os

class MySettings:
    # Path to the database in the 'instance' folder
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getcwd(), 'app', 'instance', 'campaign.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
