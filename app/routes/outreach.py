from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.outreach import create_outreach_model
from app.models.factory import get_model

Outreach = create_outreach_model(db)
outreach_bp = Blueprint('outreach', __name__)

class OutreachSchema(Schema):
    """Marshmallow schema for validating outreach input"""
    contact_id = fields.Integer(required=True)
    outreach_type = fields.String(
        required=True, 
        validate=[
            validate.Length(min=2, max=50),
            validate.OneOf([
                'Phone', 
                'Email', 
                'SMS', 
                'Door-to-Door', 
                'Social Media', 
                'Mail'
            ])
        ]
    )
    notes = fields.String(validate=validate.Length(max=500), required=False, allow_none=True)
    timestamp = fields.DateTime(required=False, allow_none=True)

@outreach_bp.route('/', methods=['GET'])
def get_all_outreach():
    """Retrieve outreach items with optional filtering"""
    # Optional filtering parameters
    contact_id = request.args.get('contact_id', type=int)
    outreach_type = request.args.get('outreach_type')
    
    # Build base query
    query = Outreach.query
    
    # Apply filters if provided
    if contact_id:
        query = query.filter_by(contact_id=contact_id)
    
    if outreach_type:
        query = query.filter(Outreach.outreach_type.ilike(f'%{outreach_type}%'))
    
    # Execute query and serialize results
    outreach_items = query.all()
    return jsonify([{
        'id': outreach.id,
        'contact_id': outreach.contact_id,
        'outreach_type': outreach.outreach_type,
        'notes': outreach.notes,
        'timestamp': outreach.timestamp.isoformat() if outreach.timestamp else None
    } for outreach in outreach_items]), 200

@outreach_bp.route('/', methods=['POST'])
def create_outreach():
    """Create a new outreach record"""
    Contact = get_model('Contact')
    schema = OutreachSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.json)
        
        # Validate that the contact exists
        contact = Contact.query.get(data['contact_id'])
        if not contact:
            return jsonify({
                "error": "Invalid contact",
                "details": f"No contact found with ID {data['contact_id']}"
            }), 404
        
        # Create new outreach record
        outreach = Outreach(
            contact_id=data['contact_id'],
            outreach_type=data['outreach_type'],
            notes=data.get('notes'),
            timestamp=data.get('timestamp') or db.func.current_timestamp()
        )
        
        db.session.add(outreach)
        db.session.commit()
        
        return jsonify({
            'message': 'Outreach created successfully',
            'outreach': {
                'id': outreach.id,
                'contact_id': outreach.contact_id,
                'outreach_type': outreach.outreach_type,
                'notes': outreach.notes,
                'timestamp': outreach.timestamp.isoformat() if outreach.timestamp else None
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
            "error": "Unable to create outreach record. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@outreach_bp.route('/<int:outreach_id>', methods=['GET'])
def get_outreach(outreach_id):
    """Retrieve a specific outreach record by ID"""
    outreach = Outreach.query.get(outreach_id)
    if not outreach:
        return jsonify({
            "error": "Outreach record not found",
            "details": f"No outreach record found with ID {outreach_id}"
        }), 404
    
    return jsonify({
        'id': outreach.id,
        'contact_id': outreach.contact_id,
        'outreach_type': outreach.outreach_type,
        'notes': outreach.notes,
        'timestamp': outreach.timestamp.isoformat() if outreach.timestamp else None
    }), 200

@outreach_bp.route('/<int:outreach_id>', methods=['PUT'])
def update_outreach(outreach_id):
    """Update an existing outreach record"""
    Contact = get_model('Contact')
    schema = OutreachSchema(partial=True)
    
    try:
        # Find existing outreach record
        outreach = Outreach.query.get(outreach_id)
        if not outreach:
            return jsonify({
                "error": "Outreach record not found",
                "details": f"No outreach record found with ID {outreach_id}"
            }), 404
        
        # Validate incoming data
        data = schema.load(request.json)
        
        # If contact_id is being changed, validate the new contact
        if 'contact_id' in data:
            contact = Contact.query.get(data['contact_id'])
            if not contact:
                return jsonify({
                    "error": "Invalid contact",
                    "details": f"No contact found with ID {data['contact_id']}"
                }), 404
        
        # Update outreach record fields
        for key, value in data.items():
            setattr(outreach, key, value)
        
        db.session.commit()
        
        return jsonify({
            "message": "Outreach record updated successfully",
            "outreach": {
                'id': outreach.id,
                'contact_id': outreach.contact_id,
                'outreach_type': outreach.outreach_type,
                'notes': outreach.notes,
                'timestamp': outreach.timestamp.isoformat() if outreach.timestamp else None
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
            "error": "Unable to update outreach record. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500