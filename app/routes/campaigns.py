from flask import Blueprint, request, current_app
from functools import wraps
from typing import Any
from marshmallow import Schema, fields, ValidationError, validates, validate
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app import db
from app.models import get_model

# Create the blueprint
campaigns_bp = Blueprint("campaigns", __name__, url_prefix="/campaigns")

def create_response(data: Any = None, message: str = None, status: int = 200) -> tuple:
    """Create a standardized API response."""
    response = {"status": "success" if status < 400 else "error"}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return response, status

def handle_errors(f):
    """Error handling decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return create_response(message=str(e), status=400)
        except IntegrityError as e:
            db.session.rollback()
            return create_response(message="Database integrity error", status=400)
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return create_response(message=str(e), status=500)
    return decorated_function

class CampaignSchema(Schema):
    """Schema for validating campaign input."""
    name = fields.String(required=True, validate=validate.Length(min=2, max=100))
    description = fields.String(validate=validate.Length(max=500), required=False, allow_none=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    status = fields.String(
        validate=validate.OneOf(['planned', 'active', 'completed']), 
        required=False, 
        missing='planned'
    )

    @validates("end_date")
    def validate_end_date(self, value):
        """Ensure end_date is after start_date."""
        start_date = self.context.get("start_date")
        
        # Convert start_date to date if it's a string
        if isinstance(start_date, str):
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError("Invalid start_date format. Use YYYY-MM-DD.")
        
        if start_date and value <= start_date:
            raise ValidationError("End date must be after start date.")

@campaigns_bp.route("", methods=["POST"])
@handle_errors
def create_campaign():
    """Create a new campaign."""
    Campaign = get_model('Campaign')
    schema = CampaignSchema()
    data = request.get_json()
    current_app.logger.info(f"Received campaign data: {data}")

    # Validate without context
    validated_data = schema.load(data)

    # Manually validate end date
    start_date = datetime.strptime(data.get('start_date'), "%Y-%m-%d").date()
    end_date = datetime.strptime(data.get('end_date'), "%Y-%m-%d").date()
    
    if end_date <= start_date:
        raise ValidationError("End date must be after start date.")

    campaign = Campaign(**validated_data)
    db.session.add(campaign)
    db.session.commit()

    return create_response(
        data=schema.dump(campaign),
        message="Campaign created successfully",
        status=201
    )

@campaigns_bp.route("", methods=["GET"])
@handle_errors
def get_all_campaigns():
    """Get all campaigns with optional filtering and pagination."""
    Campaign = get_model('Campaign')
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    query = Campaign.query

    # Filtering
    if status := request.args.get("status"):
        if status == "active":
            query = query.filter(Campaign.end_date >= datetime.now().date())
        elif status == "completed":
            query = query.filter(Campaign.end_date < datetime.now().date())

    if search := request.args.get("search"):
        query = query.filter(Campaign.name.ilike(f"%{search}%"))

    # Sorting
    sort_by = request.args.get("sort_by", "start_date")
    sort_order = request.args.get("sort_order", "desc")
    if hasattr(Campaign, sort_by):
        query = query.order_by(getattr(Campaign, sort_by).desc() if sort_order == "desc" else getattr(Campaign, sort_by))
    else:
        return create_response(message=f"Invalid sort field: {sort_by}", status=400)

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    schema = CampaignSchema(many=True)

    return create_response(
        data={
            "campaigns": schema.dump(pagination.items),
            "meta": {
                "page": page,
                "per_page": per_page,
                "total_pages": pagination.pages,
                "total_items": pagination.total
            }
        }
    )

@campaigns_bp.route("/<int:campaign_id>", methods=["GET"])
@handle_errors
def get_campaign(campaign_id: int):
    """Get a specific campaign."""
    Campaign = get_model('Campaign')
    campaign = Campaign.query.get_or_404(campaign_id)
    schema = CampaignSchema()
    return create_response(data=schema.dump(campaign))

@campaigns_bp.route("/<int:campaign_id>", methods=["PATCH"])
@handle_errors
def update_campaign(campaign_id: int):
    """Update a campaign."""
    Campaign = get_model('Campaign')
    campaign = Campaign.query.get_or_404(campaign_id)
    schema = CampaignSchema(partial=True)
    data = schema.load(
        request.get_json(), 
        context={"start_date": request.get_json().get('start_date') if request.get_json() else None}
    )

    for key, value in data.items():
        setattr(campaign, key, value)
    db.session.commit()

    return create_response(
        data=schema.dump(campaign),
        message="Campaign updated successfully"
    )

@campaigns_bp.route("/<int:campaign_id>", methods=["DELETE"])
@handle_errors
def delete_campaign(campaign_id: int):
    """Delete a campaign."""
    Campaign = get_model('Campaign')
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()

    return create_response(message="Campaign deleted successfully")

@campaigns_bp.route("/<int:campaign_id>/stats", methods=["GET"])
@handle_errors
def get_campaign_stats(campaign_id: int):
    """Get statistics for a specific campaign."""
    Campaign = get_model('Campaign')
    campaign = Campaign.query.get_or_404(campaign_id)

    stats = {
        "total_teams": len(campaign.campaign_teams) if campaign.campaign_teams else 0,
        "total_events": len(campaign.events) if campaign.events else 0,
        "total_volunteers": len(campaign.volunteers) if campaign.volunteers else 0,
        "days_remaining": (campaign.end_date.date() - datetime.now().date()).days if campaign.end_date else None
    }

    return create_response(data=stats)