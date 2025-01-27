from flask import Blueprint, jsonify, request
from app.models import db, Citizen, Campaign

main = Blueprint('main', __name__)

# Routes for Citizen CRUD operations

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

# Routes for Campaign CRUD operations

@main.route('/campaigns', methods=['POST'])
def create_campaign():
    data = request.json
    new_campaign = Campaign(name=data['name'])
    db.session.add(new_campaign)
    db.session.commit()
    return jsonify({"message": "Campaign created", "campaign": {
        "id": new_campaign.id,
        "name": new_campaign.name
    }}), 201

@main.route('/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = Campaign.query.all()
    return jsonify([{ "id": c.id, "name": c.name } for c in campaigns])

@main.route('/campaigns/<int:id>', methods=['GET'])
def get_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    return jsonify({ "id": campaign.id, "name": campaign.name })

@main.route('/campaigns/<int:id>', methods=['PUT'])
def update_campaign(id):
    data = request.json
    campaign = Campaign.query.get_or_404(id)
    campaign.name = data.get('name', campaign.name)
    db.session.commit()
    return jsonify({"message": "Campaign updated", "campaign": {
        "id": campaign.id,
        "name": campaign.name
    }})

@main.route('/campaigns/<int:id>', methods=['DELETE'])
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({"message": "Campaign deleted"})
