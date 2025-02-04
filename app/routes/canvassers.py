from flask import Blueprint, request, current_app
from marshmallow import Schema, fields, validates, validate, ValidationError
from app import db
from app.models.factory import get_model
from datetime import datetime
from typing import Any
from functools import wraps

# Create blueprint first
canvassers_bp = Blueprint('canvassers', __name__)

def get_canvasser_model():
    """Lazy load the Canvasser model"""
    return get_model('Canvasser')

class CanvasserSchema(Schema):
    """Validation schema for Canvasser data"""
    citizen_id = fields.Integer(required=True)
    previous_intention = fields.String(validate=validate.OneOf(['undecided', 'for', 'against', 'leaning_for', 'leaning_against']))
    current_intention = fields.String(validate=validate.OneOf(['undecided', 'for', 'against', 'leaning_for', 'leaning_against']))
    last_contact_date = fields.DateTime(allow_none=True)
    notes = fields.String(allow_none=True)
    
    @validates('current_intention')
    def validate_intention_change(self, value: str):
        """Validate intention changes are tracked properly"""
        previous_intention = self.data.get('previous_intention')
        if previous_intention and value == previous_intention:
            raise ValidationError('Current intention cannot be the same as previous intention')

def create_response(data: Any = None, message: str = None, status: int = 200) -> tuple:
    """Create standardized API response"""
    response = {"status": "success" if status < 400 else "error"}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return response, status

def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return create_response(message=str(e), status=500)
    return decorated_function

@canvassers_bp.route('/', methods=['GET'])
@handle_errors
def get_all_canvassers():
    """Get all canvassers with optional filtering and pagination"""
    Canvasser = get_canvasser_model()
    
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build query
    query = Canvasser.query
    
    # Apply filters
    if current_intention := request.args.get('current_intention'):
        query = query.filter_by(current_intention=current_intention)
        
    if citizen_id := request.args.get('citizen_id', type=int):
        query = query.filter_by(citizen_id=citizen_id)
        
    if date_after := request.args.get('date_after'):
        query = query.filter(Canvasser.last_contact_date >= datetime.fromisoformat(date_after))
    
    if date_before := request.args.get('date_before'):
        query = query.filter(Canvasser.last_contact_date <= datetime.fromisoformat(date_before))

    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    schema = CanvasserSchema(many=True)
    
    return create_response(
        data={
            "canvassers": schema.dump(pagination.items),
            "meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total
            }
        }
    )

@canvassers_bp.route('/', methods=['POST'])
@handle_errors
def create_canvasser():
    """Create a new canvasser"""
    Canvasser = get_canvasser_model()
    schema = CanvasserSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return create_response(message=str(e), status=400)

    # Check if canvasser already exists for this citizen
    existing_canvasser = Canvasser.query.filter_by(citizen_id=data['citizen_id']).first()
    if existing_canvasser:
        return create_response(
            message="A canvasser record already exists for this citizen",
            status=400
        )

    canvasser = Canvasser(**data)
    db.session.add(canvasser)
    db.session.commit()

    return create_response(
        data=schema.dump(canvasser),
        message="Canvasser created successfully",
        status=201
    )

@canvassers_bp.route('/<int:canvasser_id>', methods=['GET'])
@handle_errors
def get_canvasser(canvasser_id: int):
    """Get a specific canvasser"""
    Canvasser = get_canvasser_model()
    canvasser = Canvasser.query.get_or_404(canvasser_id)
    schema = CanvasserSchema()
    return create_response(data=schema.dump(canvasser))

@canvassers_bp.route('/<int:canvasser_id>', methods=['PATCH'])
@handle_errors
def update_canvasser(canvasser_id: int):
    """Update a canvasser"""
    Canvasser = get_canvasser_model()
    canvasser = Canvasser.query.get_or_404(canvasser_id)
    schema = CanvasserSchema(partial=True)
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as e:
        return create_response(message=str(e), status=400)

    # If intention is changing, update previous intention
    if 'current_intention' in data and data['current_intention'] != canvasser.current_intention:
        data['previous_intention'] = canvasser.current_intention

    for key, value in data.items():
        setattr(canvasser, key, value)
        
    db.session.commit()
    return create_response(
        data=schema.dump(canvasser),
        message="Canvasser updated successfully"
    )

@canvassers_bp.route('/<int:canvasser_id>', methods=['DELETE'])
@handle_errors
def delete_canvasser(canvasser_id: int):
    """Delete a canvasser"""
    Canvasser = get_canvasser_model()
    canvasser = Canvasser.query.get_or_404(canvasser_id)
    db.session.delete(canvasser)
    db.session.commit()
    return create_response(message="Canvasser deleted successfully")

@canvassers_bp.route('/stats', methods=['GET'])
@handle_errors
def get_canvassing_stats():
    """Get canvassing statistics"""
    Canvasser = get_canvasser_model()
    stats = {
        "total_canvassers": Canvasser.query.count(),
        "intention_breakdown": {
            "for": Canvasser.query.filter_by(current_intention='for').count(),
            "against": Canvasser.query.filter_by(current_intention='against').count(),
            "undecided": Canvasser.query.filter_by(current_intention='undecided').count(),
            "leaning_for": Canvasser.query.filter_by(current_intention='leaning_for').count(),
            "leaning_against": Canvasser.query.filter_by(current_intention='leaning_against').count(),
        },
        "recent_contacts": Canvasser.query.filter(
            Canvasser.last_contact_date >= datetime.now().replace(hour=0, minute=0)
        ).count()
    }
    
    return create_response(data=stats)