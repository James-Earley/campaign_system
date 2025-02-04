import importlib
import re
import logging
from typing import Dict, Any
from flask import Blueprint
from sqlalchemy.orm import configure_mappers

logger = logging.getLogger(__name__)

class ModelFactory:
    """
    Singleton factory for managing model initialization and route registration.
    """
    _instance = None
    _initialized = False
    _models = {}
    _blueprints = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelFactory, cls).__new__(cls)
        return cls._instance

    def initialize(self, db, app=None):
        """Initialize models and register routes."""
        if self._initialized:
            logger.warning("ModelFactory is already initialized. Skipping.")
            return

        try:
            # First initialize models
            self._initialize_models(db)
            self._initialized = True
            logger.info("Models initialized successfully.")

            # Then register routes if app is provided
            if app:
                with app.app_context():
                    logger.info("Creating all tables in the database.")
                    db.create_all()
                    self._register_routes(app)

            logger.info("Model factory initialization complete.")
        except Exception as e:
            self._initialized = False
            self._models.clear()
            self._blueprints.clear()
            logger.error(f"Failed to initialize ModelFactory: {e}")
            raise

    def _initialize_models(self, db):
        """Initialize all models in the correct dependency order."""
        def camel_to_snake(name):
            return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

        # ✅ Fix: Ensure correct initialization order
        model_creators = [
            ('Address', 'create_address_model'),
            ('Citizen', 'create_citizen_model'),
            ('CampaignTeam', 'create_campaign_team_model'),
            ('Event', 'create_event_model'),
            ('VolunteerAssignment', 'create_volunteer_assignment_model'),
            ('Volunteer', 'create_volunteer_model'),

            # ✅ Fix: Move `CampaignEvent` before `Campaign`
            ('CampaignEvent', 'create_campaign_event_model'),
            ('Campaign', 'create_campaign_model'),  # Campaign now initializes AFTER CampaignEvent

            ('CanvassingSession', 'create_canvassing_session_model'),
            ('Donation', 'create_donation_model'),
            ('Outreach', 'create_outreach_model'),
            ('Contact', 'create_contact_model'),
            ('VotingIntention', 'create_voting_intention_model'),
            ('Voter', 'create_voter_model'),
            ('Canvasser', 'create_canvasser_model'),
            ('EventStaffer', 'create_event_staffer_model'),
        ]

        for model_name, creator_function in model_creators:
            try:
                module_name = camel_to_snake(model_name)
                module = importlib.import_module(f"app.models.{module_name}")
                create_model_func = getattr(module, creator_function)
                
                model_name, model_class = create_model_func(db, self._models)  
                if model_class is not None:
                    self._models[model_name] = model_class  
                    logger.info(f"Initialized model: {model_name}")
                else:
                    logger.warning(f"Model {model_name} initialization returned None")
            except Exception as e:
                logger.error(f"Error initializing model {model_name}: {e}")
                raise

        # ✅ Force SQLAlchemy to recognize relationships
        configure_mappers()
        logger.info("SQLAlchemy models successfully configured.")

    def _register_routes(self, app):
        """Register all route blueprints."""
        blueprint_configs = {
            'main': {'url_prefix': '/', 'blueprint_var': 'main_bp'},
            'addresses': {'url_prefix': '/api/addresses', 'blueprint_var': 'bp'},
            'campaign_team': {'url_prefix': '/api/campaign-team', 'blueprint_var': 'bp'},
            'campaigns': {'url_prefix': '/api/campaigns', 'blueprint_var': 'bp'},
            'canvassers': {'url_prefix': '/api/canvassers', 'blueprint_var': 'bp'},
            'canvassing': {'url_prefix': '/api/canvassing', 'blueprint_var': 'bp'},
            'citizens': {'url_prefix': '/api/citizens', 'blueprint_var': 'bp'},
            'donations': {'url_prefix': '/api/donations', 'blueprint_var': 'bp'},
            'event_staffers': {'url_prefix': '/api/event-staffers', 'blueprint_var': 'bp'},
            'events': {'url_prefix': '/api/events', 'blueprint_var': 'bp'},
            'outreach': {'url_prefix': '/api/outreach', 'blueprint_var': 'bp'},
            'volunteers': {'url_prefix': '/api/volunteers', 'blueprint_var': 'bp'},
            'voters': {'url_prefix': '/api/voters', 'blueprint_var': 'bp'}
        }

        for blueprint_name, config in blueprint_configs.items():
            try:
                module = importlib.import_module(f"app.routes.{blueprint_name}")
                blueprint = None
                
                try:
                    if hasattr(module, 'create_blueprint') and callable(getattr(module, 'create_blueprint')):
                        # If the module has a create_blueprint function, call it with models
                        blueprint = module.create_blueprint(self._models)
                    else:
                        # Try multiple possible blueprint names
                        possible_names = [
                            config['blueprint_var'],
                            'bp',
                            f'{blueprint_name}_bp',
                            f'{blueprint_name.replace("_", "")}_bp'
                        ]
                        
                        for name in possible_names:
                            if hasattr(module, name) and isinstance(getattr(module, name), Blueprint):
                                blueprint = getattr(module, name)
                                break
                            
                    if blueprint is None:
                        logger.warning(f"Blueprint {blueprint_name} missing required blueprint variable. Tried: {', '.join(possible_names)}")
                        return
                        
                    # Register the blueprint if we found one
                    app.register_blueprint(blueprint, url_prefix=config['url_prefix'])
                    self._blueprints[blueprint_name] = blueprint
                    logger.info(f"Registered blueprint: {blueprint_name} at {config['url_prefix']}")
                        
                except AttributeError as e:
                    logger.error(f"Error accessing blueprint attributes for {blueprint_name}: {e}")
                except Exception as e:
                    logger.error(f"Error setting up blueprint {blueprint_name}: {e}")
                    
            except ImportError as e:
                logger.warning(f"Optional blueprint {blueprint_name} not found: {e}")
            except Exception as e:
                logger.error(f"Error registering blueprint {blueprint_name}: {e}")

    def get_model(self, model_name: str):
        """Get a model by name."""
        if not self._initialized:
            raise RuntimeError("ModelFactory not initialized. Call initialize() first.")
        
        model = self._models.get(model_name)
        if model is None:
            raise ValueError(f"Model '{model_name}' not found.")
            
        return model

    def clear_cache(self):
        """Clear the model and blueprint cache."""
        self._models.clear()
        self._blueprints.clear()
        self._initialized = False
        logger.info("ModelFactory cache cleared.")

# Ensure the factory is instantiated
model_factory = ModelFactory()

def get_model(model_name: str):
    return model_factory.get_model(model_name)
