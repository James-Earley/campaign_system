def initialize_models(db):
    from .citizen import create_citizen_model
    from .campaign import create_campaign_model
    from .donation import create_donation_model

    Citizen = create_citizen_model(db)
    Campaign = create_campaign_model(db)
    Donation = create_donation_model(db)

    return Citizen, Campaign, Donation
