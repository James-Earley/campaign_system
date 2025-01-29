from flask import Blueprint, jsonify, request
from app import db
from datetime import datetime

campaigns_bp = Blueprint('campaigns', __name__)

# Function to get Campaign model dynamically
def get_campaign_model():
    from app.models import initialize_models
    Campaign, _, _ = initialize_models(db)  # Load Campaign model
    return Campaign

# GET /api/v1/campaigns - List all campaigns
@campaigns_bp.route('/', methods=['GET'])
def get_campaigns():
    Campaign = get_campaign_model()  # Ensure Campaign is loaded
    campaigns = Campaign.query.all()
    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "start_date": c.start_date.isoformat(),
            "end_date": c.end_date.isoformat() if c.end_date else None,
            "description": c.description
        }
        for c in campaigns
    ]), 200

# POST /api/v1/campaigns - Create a new campaign
@campaigns_bp.route('/', methods=['POST'])
def create_campaign():
    Campaign = get_campaign_model()
    data = request.get_json()
    
    try:
        # Parse and validate dates
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    campaign = Campaign(
        name=data['name'],
        description=data.get('description'),
        start_date=start_date,
        end_date=end_date
    )
    db.session.add(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign created successfully!", "campaign": {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "description": campaign.description
    }}), 201

# GET /api/v1/campaigns/<int:id> - Get a specific campaign by ID
@campaigns_bp.route('/<int:id>', methods=['GET'])
def get_campaign(id):
    Campaign = get_campaign_model()
    campaign = Campaign.query.get_or_404(id)
    return jsonify({
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "description": campaign.description
    }), 200

# PUT /api/v1/campaigns/<int:id> - Update a specific campaign
@campaigns_bp.route('/<int:id>', methods=['PUT'])
def update_campaign(id):
    Campaign = get_campaign_model()
    campaign = Campaign.query.get_or_404(id)
    data = request.get_json()
    
    try:
        # Update and validate dates
        campaign.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else campaign.start_date
        campaign.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else campaign.end_date
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Update other fields
    campaign.name = data.get('name', campaign.name)
    campaign.description = data.get('description', campaign.description)

    db.session.commit()
    return jsonify({"message": "Campaign updated successfully!", "campaign": {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "description": campaign.description
    }}), 200

# DELETE /api/v1/campaigns/<int:id> - Delete a specific campaign
@campaigns_bp.route('/<int:id>', methods=['DELETE'])
def delete_campaign(id):
    Campaign = get_campaign_model()
    campaign = Campaign.query.get_or_404(id)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted successfully!"}), 200
