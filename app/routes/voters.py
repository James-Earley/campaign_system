from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime
from app import db
from app.models.factory import get_model

voters_bp = Blueprint('voters', __name__)

class VoterSchema(Schema):
    """Marshmallow schema for validating voter input"""
    citizen_id = fields.Integer(required=True)
    registration_date = fields.Date(required=True)
    last_known_vote_intention = fields.String(
        required=False, 
        validate=validate.OneOf([
            'Undecided', 
            'Strongly Support', 
            'Somewhat Support', 
            'Neutral', 
            'Somewhat Oppose', 
            'Strongly Oppose'
        ]),
        missing=None
    )
    last_intention_change_date = fields.Date(required=False, allow_none=True)

@voters_bp.route('/', methods=['GET'])
def get_voters():
    """Retrieve voters with optional filtering"""
    Voter = get_model('Voter')
    
    # Optional filtering parameters
    citizen_id = request.args.get('citizen_id', type=int)
    vote_intention = request.args.get('vote_intention')
    min_registration_date = request.args.get('min_registration_date')
    max_registration_date = request.args.get('max_registration_date')
    
    # Build base query
    query = Voter.query
    
    # Apply filters if provided
    if citizen_id:
        query = query.filter_by(citizen_id=citizen_id)
    
    if vote_intention:
        query = query.filter(Voter.last_known_vote_intention == vote_intention)
    
    if min_registration_date:
        try:
            min_date = datetime.strptime(min_registration_date, '%Y-%m-%d').date()
            query = query.filter(Voter.registration_date >= min_date)
        except ValueError:
            return jsonify({
                "error": "Invalid min_registration_date format",
                "details": "Date must be in YYYY-MM-DD format"
            }), 400
    
    if max_registration_date:
        try:
            max_date = datetime.strptime(max_registration_date, '%Y-%m-%d').date()
            query = query.filter(Voter.registration_date <= max_date)
        except ValueError:
            return jsonify({
                "error": "Invalid max_registration_date format",
                "details": "Date must be in YYYY-MM-DD format"
            }), 400
    
    # Execute query and serialize results
    voters = query.all()
    return jsonify([{
        "id": voter.voter_id,
        "citizen_id": voter.citizen_id,
        "registration_date": voter.registration_date.isoformat(),
        "last_known_vote_intention": voter.last_known_vote_intention,
        "last_intention_change_date": voter.last_intention_change_date.isoformat() if voter.last_intention_change_date else None
    } for voter in voters]), 200

@voters_bp.route('/', methods=['POST'])
def create_voter():
    """Create a new voter record"""
    Voter = get_model('Voter')
    Citizen = get_model('Citizen')
    schema = VoterSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # Validate that the citizen exists
        citizen = Citizen.query.get(data['citizen_id'])
        if not citizen:
            return jsonify({
                "error": "Invalid citizen",
                "details": f"No citizen found with ID {data['citizen_id']}"
            }), 404
        
        # Check for existing voter record
        existing_voter = Voter.query.filter_by(citizen_id=data['citizen_id']).first()
        if existing_voter:
            return jsonify({
                "error": "Duplicate voter",
                "details": f"Voter for citizen ID {data['citizen_id']} already exists"
            }), 409
        
        # Create new voter
        voter = Voter(
            citizen_id=data['citizen_id'],
            registration_date=data['registration_date'],
            last_known_vote_intention=data.get('last_known_vote_intention'),
            last_intention_change_date=data.get('last_intention_change_date')
        )
        
        db.session.add(voter)
        db.session.commit()
        
        return jsonify({
            "message": "Voter added successfully!",
            "voter": {
                "id": voter.voter_id,
                "citizen_id": voter.citizen_id,
                "registration_date": voter.registration_date.isoformat(),
                "last_known_vote_intention": voter.last_known_vote_intention,
                "last_intention_change_date": voter.last_intention_change_date.isoformat() if voter.last_intention_change_date else None
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
            "error": "Unable to add voter. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@voters_bp.route('/<int:voter_id>', methods=['GET'])
def get_voter(voter_id):
    """Retrieve a specific voter by ID"""
    Voter = get_model('Voter')
    
    voter = Voter.query.get(voter_id)
    if not voter:
        return jsonify({
            "error": "Voter not found",
            "details": f"No voter found with ID {voter_id}"
        }), 404
    
    return jsonify({
        "id": voter.voter_id,
        "citizen_id": voter.citizen_id,
        "registration_date": voter.registration_date.isoformat(),
        "last_known_vote_intention": voter.last_known_vote_intention,
        "last_intention_change_date": voter.last_intention_change_date.isoformat() if voter.last_intention_change_date else None
    }), 200

@voters_bp.route('/<int:voter_id>', methods=['PUT'])
def update_voter(voter_id):
    """Update an existing voter record"""
    Voter = get_model('Voter')
    Citizen = get_model('Citizen')
    schema = VoterSchema(partial=True)
    
    try:
        # Find existing voter
        voter = Voter.query.get(voter_id)
        if not voter:
            return jsonify({
                "error": "Voter not found",
                "details": f"No voter found with ID {voter_id}"
            }), 404
        
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # If citizen_id is being changed, validate the new citizen
        if 'citizen_id' in data:
            citizen = Citizen.query.get(data['citizen_id'])
            if not citizen:
                return jsonify({
                    "error": "Invalid citizen",
                    "details": f"No citizen found with ID {data['citizen_id']}"
                }), 404
        
        # Update voter fields
        for key, value in data.items():
            setattr(voter, key, value)
        
        db.session.commit()
        
        return jsonify({
            "message": "Voter updated successfully",
            "voter": {
                "id": voter.voter_id,
                "citizen_id": voter.citizen_id,
                "registration_date": voter.registration_date.isoformat(),
                "last_known_vote_intention": voter.last_known_vote_intention,
                "last_intention_change_date": voter.last_intention_change_date.isoformat() if voter.last_intention_change_date else None
            }
        }), 200
    
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
            "error": "Unable to update voter. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500