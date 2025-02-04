from typing import Dict, List
from flask import Flask, Blueprint
from importlib import import_module
from typing import TypedDict

class BlueprintConfig(TypedDict):
    url_prefix: str
    description: str
    module_path: str

# Define blueprint configurations with module paths
BLUEPRINT_CONFIGS: Dict[str, BlueprintConfig] = {
    'addresses': {
        'url_prefix': '/api/v1/addresses',
        'description': 'Address management endpoints',
        'module_path': 'app.routes.addresses'
    },
    'main': {
        'url_prefix': '/',
        'description': 'Main application routes',
        'module_path': 'app.routes.main'
    },
    'citizens': {
        'url_prefix': '/api/v1/citizens',
        'description': 'Citizen management endpoints',
        'module_path': 'app.routes.citizens'
    },
    'campaigns': {
        'url_prefix': '/api/v1/campaigns',
        'description': 'Campaign management endpoints',
        'module_path': 'app.routes.campaigns'
    },
    'events': {
        'url_prefix': '/api/v1/events',
        'description': 'Event management endpoints',
        'module_path': 'app.routes.events'
    },
    'donations': {
        'url_prefix': '/api/v1/donations',
        'description': 'Donation tracking endpoints',
        'module_path': 'app.routes.donations'
    },
    'volunteers': {
        'url_prefix': '/api/v1/volunteers',
        'description': 'Volunteer management endpoints',
        'module_path': 'app.routes.volunteers'
    },
    'canvassing': {
        'url_prefix': '/api/v1/canvassing',
        'description': 'Canvassing operation endpoints',
        'module_path': 'app.routes.canvassing'
    },
    'campaign_team': {
        'url_prefix': '/api/v1/campaign-team', 
        'description': 'Campaign team management endpoints',
        'module_path': 'app.routes.campaign_team'
    },
    'canvassers': {
        'url_prefix': '/api/v1/canvassers',
        'description': 'Canvasser management endpoints',
        'module_path': 'app.routes.canvassers'
    },
    'event_staffers': {
        'url_prefix': '/api/v1/event-staffers',
        'description': 'Event staff management endpoints',
        'module_path': 'app.routes.event_staffers'
    },
    'outreach': {
        'url_prefix': '/api/v1/outreach',
        'description': 'Outreach management endpoints',
        'module_path': 'app.routes.outreach'
    },
    'voters': {
        'url_prefix': '/api/v1/voters',
        'description': 'Voters management endpoints',
        'module_path': 'app.routes.voters'
    }
}

def register_blueprints(app: Flask) -> List[str]:
    """
    Lazily register all blueprints with the application.
    
    Args:
        app: Flask application instance
        
    Returns:
        List of registered blueprint names
        
    Raises:
        Exception: If blueprint registration fails
    """
    registered: List[str] = []
    
    for blueprint_name, config in BLUEPRINT_CONFIGS.items():
        try:
            # Lazily import the blueprint module
            module = import_module(config['module_path'])
            
            # Get the blueprint instance using naming convention
            blueprint = getattr(module, f"{blueprint_name}_bp")
            
            # Register blueprint with its configuration
            app.register_blueprint(
                blueprint,
                url_prefix=config['url_prefix']
            )
            registered.append(blueprint_name)
            
        except Exception as e:
            app.logger.error(
                f"Failed to register blueprint {blueprint_name}: {str(e)}",
                exc_info=True
            )
            raise
            
    app.logger.info(f"Successfully registered blueprints: {', '.join(registered)}")
    return registered

def get_route_documentation() -> Dict[str, str]:
    """
    Get documentation for all routes.
    
    Returns:
        Dictionary mapping blueprint names to their descriptions
    """
    return {
        name: config['description']
        for name, config in BLUEPRINT_CONFIGS.items()
    }