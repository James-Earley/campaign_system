from flask import Blueprint

from .citizens import citizens_bp
from .campaigns import campaigns_bp

# New homepage blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return "Welcome to the Campaign Management System!", 200

__all__ = ['citizens_bp', 'campaigns_bp']
