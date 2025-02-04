from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime
from app import db
from app.models.factory import get_model

donations_bp = Blueprint('donations', __name__)

class DonationSchema(Schema):
    """Marshmallow schema for validating donation input"""
    citizen_id = fields.Integer(required=True)
    campaign_id = fields.Integer(required=True)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0))

@donations_bp.route('/', methods=['POST'])
def create_donation():
    """Create a new donation"""
    Donation = get_model('Donation')
    Citizen = get_model('Citizen')
    Campaign = get_model('Campaign')
    schema = DonationSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # Validate related entities exist
        citizen = Citizen.query.get(data['citizen_id'])
        if not citizen:
            return jsonify({
                "error": "Invalid citizen",
                "details": f"No citizen found with ID {data['citizen_id']}"
            }), 404
        
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return jsonify({
                "error": "Invalid campaign",
                "details": f"No campaign found with ID {data['campaign_id']}"
            }), 404
        
        # Create new donation
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
                "amount": str(new_donation.amount),
                "donation_date": new_donation.donation_date.isoformat()
            }
        }), 201
    
    except ValidationError as err:
        # Handle validation errors
        return jsonify({
            "error": "Validation failed", 
            "details": err.messages
        }), 400
    
    except IntegrityError:
        # Handle database integrity errors
        db.session.rollback()
        return jsonify({
            "error": "Unable to record donation. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@donations_bp.route('/', methods=['GET'])
def get_donations():
    """Retrieve donations with optional filtering"""
    Donation = get_model('Donation')
    
    # Optional filtering parameters
    citizen_id = request.args.get('citizen_id', type=int)
    campaign_id = request.args.get('campaign_id', type=int)
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    
    # Build base query
    query = Donation.query
    
    # Apply filters if provided
    if citizen_id:
        query = query.filter_by(citizen_id=citizen_id)
    
    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)
    
    if min_amount is not None:
        query = query.filter(Donation.amount >= min_amount)
    
    if max_amount is not None:
        query = query.filter(Donation.amount <= max_amount)
    
    # Execute query and serialize results
    donations = query.all()
    return jsonify([{
        "id": d.id,
        "citizen_id": d.citizen_id,
        "campaign_id": d.campaign_id,
        "amount": str(d.amount),
        "donation_date": d.donation_date.isoformat()
    } for d in donations]), 200

@donations_bp.route('/total', methods=['GET'])
def get_total_donations():
    """Get total donations, optionally filtered"""
    Donation = get_model('Donation')
    
    # Optional filtering parameters
    campaign_id = request.args.get('campaign_id', type=int)
    
    # Build base query
    query = db.session.query(db.func.sum(Donation.amount))
    
    # Apply campaign filter if provided
    if campaign_id:
        query = query.filter(Donation.campaign_id == campaign_id)
    
    # Execute query
    total = query.scalar() or 0
    
    return jsonify({
        "total_donations": str(total),
        "campaign_id": campaign_id
    }), 200