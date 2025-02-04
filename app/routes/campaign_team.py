from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import get_model  # Use get_model instead of direct import
from app.models.enums import VolunteerStatus
from datetime import datetime

# Create the blueprint
campaign_team_bp = Blueprint('campaign_team', __name__)

def team_to_dict(team):
    """Convert team object to dictionary"""
    return {
        'id': team.id,
        'campaign_id': team.campaign_id,
        'name': team.name,
        'description': team.description,
        'contact_email': team.contact_email,
        'contact_phone': team.contact_phone,
        'team_size': team.team_size,
        'staff_type': team.staff_type if hasattr(team, 'staff_type') else None,
        'status': team.status.value if hasattr(team, 'status') else None,
        'created_at': team.created_at.isoformat() if team.created_at else None,
        'updated_at': team.updated_at.isoformat() if team.updated_at else None
    }

@campaign_team_bp.route('/', methods=['GET'])
def get_campaign_teams():
    """Get all campaign teams with optional filters"""
    try:
        # Get the model through the factory
        CampaignTeam = get_model('CampaignTeam')
        
        # Get query parameters
        campaign_id = request.args.get('campaign_id', type=int)
        staff_type = request.args.get('staff_type')
        status = request.args.get('status')
        
        # Start with base query
        query = CampaignTeam.query
        
        # Apply filters if provided
        if campaign_id:
            query = query.filter_by(campaign_id=campaign_id)
        if staff_type:
            query = query.filter_by(staff_type=staff_type)
        if status and hasattr(CampaignTeam, 'status'):
            try:
                status_enum = VolunteerStatus[status.upper()]
                query = query.filter_by(status=status_enum)
            except KeyError:
                return jsonify({'error': f'Invalid status: {status}'}), 400
        
        teams = query.all()
        return jsonify([team_to_dict(team) for team in teams])
        
    except Exception as e:
        current_app.logger.error(f"Error fetching campaign teams: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_team_bp.route('/campaign-team/<int:team_id>', methods=['GET'])
def get_campaign_team(team_id):
    """Get a specific campaign team by ID"""
    try:
        CampaignTeam = get_model('CampaignTeam')
        team = CampaignTeam.query.get_or_404(team_id)
        return jsonify(team_to_dict(team))
    except Exception as e:
        current_app.logger.error(f"Error fetching campaign team {team_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_team_bp.route('/campaign-team', methods=['POST'])
def create_campaign_team():
    """Create a new campaign team"""
    try:
        CampaignTeam = get_model('CampaignTeam')
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['campaign_id', 'name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create new team with only the fields that exist in the model
        team_data = {
            'campaign_id': data['campaign_id'],
            'name': data['name'],
            'description': data.get('description'),
            'contact_email': data.get('contact_email'),
            'contact_phone': data.get('contact_phone'),
            'team_size': data.get('team_size')
        }
        
        # Only add staff_type and status if they exist in the model
        if hasattr(CampaignTeam, 'staff_type'):
            team_data['staff_type'] = data.get('staff_type')
        if hasattr(CampaignTeam, 'status') and 'status' in data:
            try:
                team_data['status'] = VolunteerStatus[data['status'].upper()]
            except KeyError:
                return jsonify({'error': f'Invalid status: {data["status"]}'}), 400
        
        new_team = CampaignTeam(**team_data)
        db.session.add(new_team)
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign team created successfully',
            'team': team_to_dict(new_team)
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Integrity error creating campaign team: {str(e)}")
        return jsonify({'error': 'Team name already exists for this campaign'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating campaign team: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_team_bp.route('/campaign-team/<int:team_id>', methods=['PUT'])
def update_campaign_team(team_id):
    """Update an existing campaign team"""
    try:
        CampaignTeam = get_model('CampaignTeam')
        team = CampaignTeam.query.get_or_404(team_id)
        data = request.get_json()
        
        # Update fields if provided and they exist in the model
        for field in ['name', 'description', 'contact_email', 'contact_phone', 'team_size']:
            if field in data:
                setattr(team, field, data[field])
        
        # Update staff_type and status only if they exist in the model
        if hasattr(team, 'staff_type') and 'staff_type' in data:
            team.staff_type = data['staff_type']
            
        if hasattr(team, 'status') and 'status' in data:
            try:
                team.status = VolunteerStatus[data['status'].upper()]
            except KeyError:
                return jsonify({'error': f'Invalid status: {data["status"]}'}), 400
        
        team.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Campaign team updated successfully',
            'team': team_to_dict(team)
        })
        
    except IntegrityError as e:
        db.session.rollback()
        current_app.logger.error(f"Integrity error updating campaign team {team_id}: {str(e)}")
        return jsonify({'error': 'Team name already exists for this campaign'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating campaign team {team_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_team_bp.route('/campaign-team/<int:team_id>', methods=['DELETE'])
def delete_campaign_team(team_id):
    """Delete a campaign team"""
    try:
        CampaignTeam = get_model('CampaignTeam')
        team = CampaignTeam.query.get_or_404(team_id)
        db.session.delete(team)
        db.session.commit()
        
        return jsonify({'message': 'Campaign team deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting campaign team {team_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@campaign_team_bp.route('/campaign/<int:campaign_id>/teams', methods=['GET'])
def get_teams_by_campaign(campaign_id):
    """Get all teams for a specific campaign"""
    try:
        CampaignTeam = get_model('CampaignTeam')
        teams = CampaignTeam.query.filter_by(campaign_id=campaign_id).all()
        return jsonify([team_to_dict(team) for team in teams])
    except Exception as e:
        current_app.logger.error(f"Error fetching teams for campaign {campaign_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500