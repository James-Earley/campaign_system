from app import db  
from .factory import model_factory, get_model  

__all__ = [
    'db',  # Add this
    'model_factory',
    'get_model'
]

# Model class name constants for type safety
MODEL_NAMES = {
    'ADDRESS': 'Address',  # Add this line
    'CITIZEN': 'Citizen',
    'VOTER': 'Voter',
    'CAMPAIGN': 'Campaign',
    'EVENT': 'Event',
    'DONATION': 'Donation',
    'VOLUNTEER': 'Volunteer',
    'CAMPAIGN_EVENT': 'CampaignEvent',
    'CAMPAIGN_TEAM': 'CampaignTeam',
    'VOLUNTEER_ASSIGNMENT': 'VolunteerAssignment',
    'CANVASSING_SESSION': 'CanvassingSession',
    'CANVASSER': 'Canvasser',
    'EVENT_STAFFER': 'EventStaffer',
    'OUTREACH': 'Outreach',
    'VOTING_INTENTION': 'VotingIntention' 
}

def get_initialized_models():
    """
    Get all initialized models from the factory.
    Returns a dictionary of model names to model classes.
    """
    return {
        model_name: get_model(model_name)
        for model_name in MODEL_NAMES.values()
    }