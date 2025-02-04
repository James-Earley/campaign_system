from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime
from app import db
from app.models.factory import get_model

events_bp = Blueprint('events', __name__)

class EventSchema(Schema):
    """Marshmallow schema for validating event input"""
    campaign_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(validate=validate.Length(max=500), required=False, allow_none=True)
    date = fields.Date(required=True)
    location = fields.String(required=True, validate=validate.Length(min=2, max=100))
    event_type = fields.String(validate=validate.Length(max=50), missing='General')
    capacity = fields.Integer(validate=validate.Range(min=0), missing=0)

@events_bp.route('/', methods=['GET'])
def get_all_events():
    """Retrieve events with optional filtering"""
    Event = get_model('Event')
    
    # Optional filtering parameters
    campaign_id = request.args.get('campaign_id', type=int)
    event_type = request.args.get('event_type')
    min_date = request.args.get('min_date')
    max_date = request.args.get('max_date')
    location = request.args.get('location')
    
    # Build base query
    query = Event.query
    
    # Apply filters if provided
    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)
    
    if event_type:
        query = query.filter(Event.event_type.ilike(f'%{event_type}%'))
    
    if min_date:
        try:
            min_date = datetime.strptime(min_date, '%Y-%m-%d').date()
            query = query.filter(Event.date >= min_date)
        except ValueError:
            return jsonify({
                "error": "Invalid min_date format",
                "details": "Date must be in YYYY-MM-DD format"
            }), 400
    
    if max_date:
        try:
            max_date = datetime.strptime(max_date, '%Y-%m-%d').date()
            query = query.filter(Event.date <= max_date)
        except ValueError:
            return jsonify({
                "error": "Invalid max_date format",
                "details": "Date must be in YYYY-MM-DD format"
            }), 400
    
    if location:
        query = query.filter(Event.location.ilike(f'%{location}%'))
    
    # Execute query and serialize results
    events = query.all()
    return jsonify([{
        'id': event.id,
        'campaign_id': event.campaign_id,
        'name': event.name,
        'description': event.description,
        'date': event.date.isoformat(),
        'location': event.location,
        'event_type': event.event_type,
        'capacity': event.capacity
    } for event in events]), 200

@events_bp.route('/', methods=['POST'])
def create_event():
    """Create a new event"""
    Event = get_model('Event')
    Campaign = get_model('Campaign')
    schema = EventSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # Validate that the campaign exists
        campaign = Campaign.query.get(data['campaign_id'])
        if not campaign:
            return jsonify({
                "error": "Invalid campaign",
                "details": f"No campaign found with ID {data['campaign_id']}"
            }), 404
        
        # Check for existing events with the same name, date, and location
        existing_event = Event.query.filter_by(
            name=data['name'],
            date=data['date'],
            location=data['location']
        ).first()
        
        if existing_event:
            return jsonify({
                "error": "Duplicate event",
                "details": "An event with the same name, date, and location already exists"
            }), 409
        
        # Create new event
        event = Event(
            campaign_id=data['campaign_id'],
            name=data['name'],
            description=data.get('description', ''),
            date=data['date'],
            location=data['location'],
            event_type=data.get('event_type', 'General'),
            capacity=data.get('capacity', 0)
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            "message": "Event created successfully!",
            "event": {
                "id": event.id,
                "campaign_id": event.campaign_id,
                "name": event.name,
                "description": event.description,
                "date": event.date.strftime('%Y-%m-%d'),
                "location": event.location,
                "event_type": event.event_type,
                "capacity": event.capacity
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
            "error": "Unable to create event. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@events_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    """Retrieve a specific event by ID"""
    Event = get_model('Event')
    
    event = Event.query.get(event_id)
    if not event:
        return jsonify({
            "error": "Event not found",
            "details": f"No event found with ID {event_id}"
        }), 404
    
    return jsonify({
        'id': event.id,
        'campaign_id': event.campaign_id,
        'name': event.name,
        'description': event.description,
        'date': event.date.isoformat(),
        'location': event.location,
        'event_type': event.event_type,
        'capacity': event.capacity
    }), 200

@events_bp.route('/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing event"""
    Event = get_model('Event')
    Campaign = get_model('Campaign')
    schema = EventSchema(partial=True)
    
    try:
        # Find existing event
        event = Event.query.get(event_id)
        if not event:
            return jsonify({
                "error": "Event not found",
                "details": f"No event found with ID {event_id}"
            }), 404
        
        # Validate incoming data
        data = schema.load(request.get_json())
        
        # If campaign_id is being changed, validate the new campaign
        if 'campaign_id' in data:
            campaign = Campaign.query.get(data['campaign_id'])
            if not campaign:
                return jsonify({
                    "error": "Invalid campaign",
                    "details": f"No campaign found with ID {data['campaign_id']}"
                }), 404
        
        # Update event fields
        for key, value in data.items():
            setattr(event, key, value)
        
        db.session.commit()
        
        return jsonify({
            "message": "Event updated successfully",
            "event": {
                "id": event.id,
                "campaign_id": event.campaign_id,
                "name": event.name,
                "description": event.description,
                "date": event.date.strftime('%Y-%m-%d'),
                "location": event.location,
                "event_type": event.event_type,
                "capacity": event.capacity
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
            "error": "Unable to update event. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500