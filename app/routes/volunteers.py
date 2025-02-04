from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields, ValidationError, validate
from datetime import datetime
from app import db
from app.models.factory import get_model

volunteers_bp = Blueprint('volunteers', __name__)

class VolunteerAssignmentSchema(Schema):
    """Marshmallow schema for validating volunteer assignment input"""
    volunteer_id = fields.Integer(required=True)
    campaign_event_id = fields.Integer(required=False, allow_none=True)
    canvassing_session_id = fields.Integer(required=False, allow_none=True)
    task = fields.String(
        required=True, 
        validate=[
            validate.Length(min=2, max=100),
            validate.OneOf([
                'Canvassing', 
                'Event Setup', 
                'Phone Banking', 
                'Data Entry', 
                'Fundraising', 
                'Social Media', 
                'Other'
            ])
        ]
    )

@volunteers_bp.route('/volunteer-assignments', methods=['POST'])
def assign_volunteer():
    """Create a new volunteer assignment"""
    VolunteerAssignment = get_model('VolunteerAssignment')
    Volunteer = get_model('Volunteer')
    Campaign = get_model('Campaign')
    CanvassingSession = get_model('CanvassingSession')
    schema = VolunteerAssignmentSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.json)
        
        # Validate volunteer existence
        volunteer = Volunteer.query.get(data['volunteer_id'])
        if not volunteer:
            return jsonify({
                "error": "Invalid volunteer",
                "details": f"No volunteer found with ID {data['volunteer_id']}"
            }), 404
        
        # Validate either campaign event or canvassing session is provided
        if not (data.get('campaign_event_id') or data.get('canvassing_session_id')):
            return jsonify({
                "error": "Validation failed",
                "details": "Either campaign_event_id or canvassing_session_id must be provided"
            }), 400
        
        # Validate campaign event if provided
        if data.get('campaign_event_id'):
            campaign_event = Campaign.query.get(data['campaign_event_id'])
            if not campaign_event:
                return jsonify({
                    "error": "Invalid campaign event",
                    "details": f"No campaign event found with ID {data['campaign_event_id']}"
                }), 404
        
        # Validate canvassing session if provided
        if data.get('canvassing_session_id'):
            canvassing_session = CanvassingSession.query.get(data['canvassing_session_id'])
            if not canvassing_session:
                return jsonify({
                    "error": "Invalid canvassing session",
                    "details": f"No canvassing session found with ID {data['canvassing_session_id']}"
                }), 404
        
        # Check for existing similar assignment
        existing_assignment = VolunteerAssignment.query.filter_by(
            volunteer_id=data['volunteer_id'],
            campaign_event_id=data.get('campaign_event_id'),
            canvassing_session_id=data.get('canvassing_session_id'),
            task=data['task']
        ).first()
        
        if existing_assignment:
            return jsonify({
                "error": "Duplicate assignment",
                "details": "This volunteer is already assigned to this task"
            }), 409
        
        # Create new assignment
        new_assignment = VolunteerAssignment(
            volunteer_id=data['volunteer_id'],
            campaign_event_id=data.get('campaign_event_id'),
            canvassing_session_id=data.get('canvassing_session_id'),
            task=data['task'],
            assigned_at=datetime.utcnow()
        )
        
        db.session.add(new_assignment)
        db.session.commit()
        
        return jsonify({
            "message": "Volunteer assigned successfully",
            "assignment": {
                "id": new_assignment.id,
                "volunteer_id": new_assignment.volunteer_id,
                "task": new_assignment.task,
                "campaign_event_id": new_assignment.campaign_event_id,
                "canvassing_session_id": new_assignment.canvassing_session_id,
                "assigned_at": new_assignment.assigned_at.isoformat()
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
            "error": "Unable to assign volunteer. Check data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@volunteers_bp.route('/volunteer-assignments', methods=['GET'])
def get_assignments():
    """Retrieve volunteer assignments with optional filtering"""
    VolunteerAssignment = get_model('VolunteerAssignment')
    
    # Optional filtering parameters
    volunteer_id = request.args.get('volunteer_id', type=int)
    task = request.args.get('task')
    campaign_event_id = request.args.get('campaign_event_id', type=int)
    canvassing_session_id = request.args.get('canvassing_session_id', type=int)
    
    # Build base query
    query = VolunteerAssignment.query
    
    # Apply filters if provided
    if volunteer_id:
        query = query.filter_by(volunteer_id=volunteer_id)
    
    if task:
        query = query.filter(VolunteerAssignment.task.ilike(f'%{task}%'))
    
    if campaign_event_id:
        query = query.filter_by(campaign_event_id=campaign_event_id)
    
    if canvassing_session_id:
        query = query.filter_by(canvassing_session_id=canvassing_session_id)
    
    # Execute query and serialize results
    assignments = query.all()
    return jsonify([{
        "id": a.id,
        "volunteer_id": a.volunteer_id,
        "task": a.task,
        "campaign_event_id": a.campaign_event_id,
        "canvassing_session_id": a.canvassing_session_id,
        "assigned_at": a.assigned_at.isoformat()
    } for a in assignments]), 200

@volunteers_bp.route('/volunteer-assignments/<int:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Retrieve a specific volunteer assignment by ID"""
    VolunteerAssignment = get_model('VolunteerAssignment')
    
    assignment = VolunteerAssignment.query.get(assignment_id)
    if not assignment:
        return jsonify({
            "error": "Volunteer assignment not found",
            "details": f"No volunteer assignment found with ID {assignment_id}"
        }), 404
    
    return jsonify({
        "id": assignment.id,
        "volunteer_id": assignment.volunteer_id,
        "task": assignment.task,
        "campaign_event_id": assignment.campaign_event_id,
        "canvassing_session_id": assignment.canvassing_session_id,
        "assigned_at": assignment.assigned_at.isoformat()
    }), 200