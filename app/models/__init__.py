# app/models/__init__.py

# Global variables for models
Citizen = None
Campaign = None
Donation = None

def initialize_models(db):
    global Citizen, Campaign, Donation

    #  Prevent multiple re-initializations
    if Citizen and Campaign and Donation:
        print(f" Returning already initialized models: {Citizen}, {Campaign}, {Donation}")
        return Citizen, Campaign, Donation

    from .citizen import create_citizen_model
    from .campaign import create_campaign_model
    from .donation import create_donation_model

    Citizen = create_citizen_model(db)
    Campaign = create_campaign_model(db)
    Donation = create_donation_model(db)

    #  Debugging output to confirm models are correctly initialized
    print(f" Models initialized: Citizen={Citizen}, Campaign={Campaign}, Donation={Donation}")

    if not Citizen or not Campaign or not Donation:
        raise RuntimeError(" Error: One or more models were not initialized correctly.")

    return Citizen, Campaign, Donation
