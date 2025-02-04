from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from app import db
from app.models.factory import get_model

event_staffers_bp = Blueprint('event_staffers', __name__)

class EventStafferSchema(Schema):
    """Marshmallow schema for validating event staffer input"""
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    role = fields.String(required=True, validate=validate.Length(min=2, max=50))
    event_id = fields.Integer(required=True)

@event_staffers_bp.route('/', methods=['GET'])
def get_event_staffers():
    """Retrieve event staffers with optional filtering"""
    EventStaffer = get_model('EventStaffer')
    
    # Optional filtering parameters
    event_id = request.args.get('event_id', type=int)
    role = request.args.get('role')
    
    # Build base query
    query = EventStaffer.query
    
    # Apply filters if provided
    if event_id:
        query = query.filter_by(event_id=event_id)
    
    if role:
        query = query.filter(EventStaffer.role.ilike(f'%{role}%'))
    
    # Execute query and serialize results
    event_staffers = query.all()
    return jsonify([{
        "id": staffer.id,
        "name": staffer.name,
        "role": staffer.role,
        "event_id": staffer.event_id
    } for staffer in event_staffers]), 200

@event_staffers_bp.route('/', methods=['POST'])
def create_event_staffer():
    """Create a new event staffer"""
    EventStaffer = get_model('EventStaffer')
    Event = get_model('Event')
    schema = EventStafferSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # Validate that the event exists
        event = Event.query.get(data['event_id'])
        if not event:
            return jsonify({
                "error": "Invalid event",
                "details": f"No event found with ID {data['event_id']}"
            }), 404
        
        # Check if staffer already exists for this event with the same name and role
        existing_staffer = EventStaffer.query.filter_by(
            name=data['name'],
            role=data['role'],
            event_id=data['event_id']
        ).first()
        
        if existing_staffer:
            return jsonify({
                "error": "Duplicate staffer",
                "details": "A staffer with the same name and role already exists for this event"
            }), 409
        
        # Create new event staffer
        staffer = EventStaffer(
            name=data['name'],
            role=data['role'],
            event_id=data['event_id']
        )
        
        db.session.add(staffer)
        db.session.commit()
        
        return jsonify({
            "message": "Event staffer added successfully!",
            "staffer": {
                "id": staffer.id,
                "name": staffer.name,
                "role": staffer.role,
                "event_id": staffer.event_id
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
            "error": "Unable to add event staffer. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@event_staffers_bp.route('/<int:staffer_id>', methods=['GET'])
def get_event_staffer(staffer_id):
    """Retrieve a specific event staffer by ID"""
    EventStaffer = get_model('EventStaffer')
    
    staffer = EventStaffer.query.get(staffer_id)
    if not staffer:
        return jsonify({
            "error": "Event staffer not found",
            "details": f"No event staffer found with ID {staffer_id}"
        }), 404
    
    return jsonify({
        "id": staffer.id,
        "name": staffer.name,
        "role": staffer.role,
        "event_id": staffer.event_id
    }), 200

@event_staffers_bp.route('/<int:staffer_id>', methods=['PUT'])
def update_event_staffer(staffer_id):
    """Update an existing event staffer"""
    EventStaffer = get_model('EventStaffer')
    Event = get_model('Event')
    schema = EventStafferSchema(partial=True)
    
    try:
        # Find existing staffer
        staffer = EventStaffer.query.get(staffer_id)
        if not staffer:
            return jsonify({
                "error": "Event staffer not found",
                "details": f"No event staffer found with ID {staffer_id}"
            }), 404
        
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # If event_id is being changed, validate the new event
        if 'event_id' in data:
            event = Event.query.get(data['event_id'])
            if not event:
                return jsonify({
                    "error": "Invalid event",
                    "details": f"No event found with ID {data['event_id']}"
                }), 404
        
        # Update staffer fields
        for key, value in data.items():
            setattr(staffer, key, value)
        
        db.session.commit()
        
        return jsonify({
            "message": "Event staffer updated successfully",
            "staffer": {
                "id": staffer.id,
                "name": staffer.name,
                "role": staffer.role,
                "event_id": staffer.event_id
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
            "error": "Unable to update event staffer. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500