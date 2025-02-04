from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.factory import get_model

citizens_bp = Blueprint('citizens', __name__)

class CitizenSchema(Schema):
    """Marshmallow schema for validating citizen input"""
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    constituency = fields.String(required=True, validate=validate.Length(min=2, max=100))

@citizens_bp.route('/', methods=['GET'])
def list_citizens():
    """Retrieve citizens with optional filtering"""
    Citizen = get_model('Citizen')
    
    # Optional filtering parameters
    name = request.args.get('name')
    constituency = request.args.get('constituency')
    
    # Build base query
    query = Citizen.query
    
    # Apply filters if provided
    if name:
        query = query.filter(Citizen.name.ilike(f'%{name}%'))
    
    if constituency:
        query = query.filter(Citizen.constituency.ilike(f'%{constituency}%'))
    
    # Execute query and serialize results
    citizens = query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "email": c.email,
        "constituency": c.constituency
    } for c in citizens]), 200

@citizens_bp.route('/', methods=['POST'])
def create_citizen():
    """Create a new citizen"""
    Citizen = get_model('Citizen')
    schema = CitizenSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.json)
        
        # Check for existing citizen with same email
        existing_citizen = Citizen.query.filter_by(email=data['email']).first()
        if existing_citizen:
            return jsonify({
                "error": "A citizen with this email already exists",
                "details": "Email must be unique"
            }), 409
        
        # Create new citizen
        new_citizen = Citizen(
            name=data['name'],
            email=data['email'],
            constituency=data['constituency']
        )
        
        db.session.add(new_citizen)
        db.session.commit()
        
        return jsonify({
            "message": "Citizen created successfully",
            "citizen": {
                "id": new_citizen.id,
                "name": new_citizen.name,
                "email": new_citizen.email,
                "constituency": new_citizen.constituency
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
            "error": "Unable to create citizen. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@citizens_bp.route('/<int:citizen_id>', methods=['GET'])
def get_citizen(citizen_id):
    """Retrieve a specific citizen by ID"""
    Citizen = get_model('Citizen')
    
    citizen = Citizen.query.get(citizen_id)
    if not citizen:
        return jsonify({
            "error": "Citizen not found",
            "details": f"No citizen found with ID {citizen_id}"
        }), 404
    
    return jsonify({
        "id": citizen.id,
        "name": citizen.name,
        "email": citizen.email,
        "constituency": citizen.constituency
    }), 200