from flask import Blueprint, jsonify, request
from app.models import db, Citizen, Campaign
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to the Campaign System"

# Citizen CRUD Operations

@main.route('/citizens', methods=['POST'])
def create_citizen():
    data = request.json
    new_citizen = Citizen(
        name=data['name'], 
        email=data['email'], 
        constituency=data['constituency']
    )
    db.session.add(new_citizen)
    db.session.commit()
    return jsonify({"message": "Citizen created", "citizen": {
        "id": new_citizen.id,
        "name": new_citizen.name,
        "email": new_citizen.email,
        "constituency": new_citizen.constituency
    }}), 201

@main.route('/citizens', methods=['GET'])
def get_citizens():
    citizens = Citizen.query.all()
    return jsonify([{ "id": c.id, "name": c.name, "email": c.email, "constituency": c.constituency } for c in citizens])

@main.route('/citizens/<int:id>', methods=['GET'])
def get_citizen(id):
    citizen = Citizen.query.get_or_404(id)
    return jsonify({ "id": citizen.id, "name": citizen.name, "email": citizen.email, "constituency": citizen.constituency })

@main.route('/citizens/<int:id>', methods=['PUT'])
def update_citizen(id):
    data = request.json
    citizen = Citizen.query.get_or_404(id)
    citizen.name = data.get('name', citizen.name)
    citizen.email = data.get('email', citizen.email)
    citizen.constituency = data.get('constituency', citizen.constituency)
    db.session.commit()
    return jsonify({"message": "Citizen updated", "citizen": {
        "id": citizen.id,
        "name": citizen.name,
        "email": citizen.email,
        "constituency": citizen.constituency
    }})

@main.route('/citizens/<int:id>', methods=['DELETE'])
def delete_citizen(id):
    citizen = Citizen.query.get_or_404(id)
    db.session.delete(citizen)
    db.session.commit()
    return jsonify({"message": "Citizen deleted"})

# Campaign CRUD Operations

main.route('/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    if 'name' not in data or 'start_date' not in data:
        return jsonify({"error": "Missing required fields: name or start_date"}), 400

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    new_campaign = Campaign(
        name=data['name'],
        start_date=start_date,
        end_date=end_date,
        description=data.get('description')
    )
    db.session.add(new_campaign)
    db.session.commit()
    return jsonify({"message": "Campaign created", "campaign": {
        "id": new_campaign.id,
        "name": new_campaign.name,
        "start_date": new_campaign.start_date.isoformat(),
        "end_date": new_campaign.end_date.isoformat() if new_campaign.end_date else None,
        "description": new_campaign.description
    }}), 201

@main.route('/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([{ "id": c.id, "name": c.name, "start_date": c.start_date.isoformat(), "end_date": c.end_date.isoformat() if c.end_date else None, "description": c.description } for c in campaigns])

@main.route('/campaigns/<int:id>', methods=['GET'])
def get_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    return jsonify({ "id": campaign.id, "name": campaign.name, "start_date": campaign.start_date.isoformat(), "end_date": campaign.end_date.isoformat() if campaign.end_date else None, "description": campaign.description })

@main.route('/campaigns/<int:id>', methods=['PUT'])
def update_campaign(id):
    data = request.json
    campaign = Campaign.query.get_or_404(id)
    try:
        campaign.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date() if 'start_date' in data else campaign.start_date
        campaign.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date() if 'end_date' in data else campaign.end_date
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    campaign.name = data.get('name', campaign.name)
    campaign.description = data.get('description', campaign.description)
    db.session.commit()
    return jsonify({"message": "Campaign updated", "campaign": {
        "id": campaign.id,
        "name": campaign.name,
        "start_date": campaign.start_date.isoformat(),
        "end_date": campaign.end_date.isoformat() if campaign.end_date else None,
        "description": campaign.description
    }})

@main.route('/campaigns/<int:id>', methods=['DELETE'])
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted"})