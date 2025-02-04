from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.factory import get_model
from app.models.enums import TaskStatus
from marshmallow import Schema, fields, ValidationError, validate

canvassing_bp = Blueprint('canvassing', __name__)

class CanvassingSessionSchema(Schema):
    """Marshmallow schema for validating canvassing session input"""
    campaign_id = fields.Integer(required=True)
    assigned_staff = fields.String(required=True)
    task_status = fields.Enum(TaskStatus, by_value=False, 
                               validate=validate.OneOf([status.name for status in TaskStatus]),
                               missing=TaskStatus.PENDING)

@canvassing_bp.route('/canvassing-sessions', methods=['POST'])
def create_canvassing_session():
    """Create a new canvassing session"""
    CanvassingSession = get_model('CanvassingSession')
    schema = CanvassingSessionSchema()
    
    try:
        # Validate incoming data
        data = schema.load(request.json)
        
        # Create new session
        new_session = CanvassingSession(
            campaign_id=data['campaign_id'],
            assigned_staff=data['assigned_staff'],
            task_status=data['task_status']
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({
            "message": "Canvassing session created", 
            "session_id": new_session.id
        }), 201
    
    except ValidationError as err:
        # Handle validation errors
        return jsonify({
            "error": "Validation failed", 
            "details": err.messages
        }), 400
    
    except IntegrityError:
        # Handle database integrity errors (e.g., foreign key constraints)
        db.session.rollback()
        return jsonify({
            "error": "Unable to create canvassing session. Check related data integrity."
        }), 422
    
    except Exception as e:
        # Catch-all for unexpected errors
        db.session.rollback()
        return jsonify({
            "error": "An unexpected error occurred", 
            "details": str(e)
        }), 500

@canvassing_bp.route('/canvassing-sessions', methods=['GET'])
def get_canvassing_sessions():
    """Retrieve all canvassing sessions"""
    CanvassingSession = get_model('CanvassingSession')
    
    # Add optional filtering
    campaign_id = request.args.get('campaign_id', type=int)
    task_status = request.args.get('task_status')
    
    # Build base query
    query = CanvassingSession.query
    
    if campaign_id:
        query = query.filter_by(campaign_id=campaign_id)
    
    if task_status:
        try:
            status = TaskStatus[task_status.upper()]
            query = query.filter_by(task_status=status)
        except KeyError:
            return jsonify({
                "error": f"Invalid task status: {task_status}"
            }), 400
    
    # Execute query and serialize results
    sessions = query.all()
    return jsonify([{
        "id": s.id,
        "campaign_id": s.campaign_id,
        "assigned_staff": s.assigned_staff,
        "task_status": s.task_status.name,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in sessions])