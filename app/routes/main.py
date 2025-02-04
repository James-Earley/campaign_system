from flask import Blueprint, jsonify, request
import logging
from app.models.factory import get_model

main_bp = Blueprint('main', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@main_bp.route('/')
def homepage():
    """Main homepage route providing system overview"""
    try:
        # Gather system statistics
        Campaign = get_model('Campaign')
        Event = get_model('Event')
        Citizen = get_model('Citizen')
        Donation = get_model('Donation')
        
        stats = {
            "total_campaigns": Campaign.query.count(),
            "total_events": Event.query.count(),
            "total_citizens": Citizen.query.count(),
            "total_donations": float(Donation.query.with_entities(
                Donation.amount.label('total')
            ).func.sum() or 0)
        }
        
        return jsonify({
            "message": "Welcome to the Campaign Management System!",
            "system_stats": stats
        }), 200
    
    except Exception as e:
        logger.error(f"Error on homepage access: {str(e)}")
        return jsonify({
            "message": "Welcome to the Campaign Management System!",
            "error": "Unable to retrieve system statistics"
        }), 500

@main_bp.route('/health')
def health_check():
    """Provide a health check endpoint for system monitoring"""
    try:
        # Perform basic database connectivity check
        Campaign = get_model('Campaign')
        Campaign.query.first()
        
        return jsonify({
            "status": "healthy",
            "message": "System is operational",
            "checks": {
                "database_connection": "OK"
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": "System health check failed",
            "error": str(e)
        }), 500

@main_bp.route('/system-info')
def system_info():
    """Provide basic system information"""
    return jsonify({
        "system_name": "Campaign Management System",
        "version": "1.0.0",
        "description": "Comprehensive campaign and event management platform",
        "available_endpoints": [
            "/",
            "/health",
            "/system-info",
            "/campaigns",
            "/events",
            "/citizens",
            "/donations",
            "/event-staffers"
        ]
    }), 200