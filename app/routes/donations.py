from flask import Blueprint, jsonify, request
from app import db
from datetime import datetime
from app.models import initialize_models

donations_bp = Blueprint('donations', __name__)  #  Correctly defining donations_bp

# Function to get Donation model dynamically
def get_donation_model():
    Citizen, Campaign, Donation = initialize_models(db)
    print(f"🚀 get_donation_model() loaded: Donation={Donation}")
    return Donation

# POST /api/v1/donations - Create a new donation
@donations_bp.route('/', methods=['POST'])
def create_donation():
    Donation = get_donation_model()
    data = request.get_json()

    if not all(key in data for key in ['citizen_id', 'campaign_id', 'amount']):
        return jsonify({"error": "Missing required fields: citizen_id, campaign_id, or amount"}), 400

    new_donation = Donation(
        citizen_id=data['citizen_id'],
        campaign_id=data['campaign_id'],
        amount=data['amount'],
        donation_date=datetime.utcnow()
    )
    db.session.add(new_donation)
    db.session.commit()

    return jsonify({
        "message": "Donation recorded successfully",
        "donation": {
            "id": new_donation.id,
            "citizen_id": new_donation.citizen_id,
            "campaign_id": new_donation.campaign_id,
            "amount": new_donation.amount,
            "donation_date": new_donation.donation_date.isoformat()
        }
    }), 201

# GET /api/v1/donations - Get all donations
@donations_bp.route('/', methods=['GET'])
def get_donations():
    Donation = get_donation_model()
    donations = Donation.query.all()
    return jsonify([
        {
            "id": d.id,
            "citizen_id": d.citizen_id,
            "campaign_id": d.campaign_id,
            "amount": d.amount,
            "donation_date": d.donation_date.isoformat()
        }
        for d in donations
    ]), 200
