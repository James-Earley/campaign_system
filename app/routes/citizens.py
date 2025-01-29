from flask import Blueprint, jsonify, request
from app.models import initialize_models
from app import db

citizens_bp = Blueprint('citizens', __name__)

# Utility to ensure the Citizen model is lazily loaded
def get_citizen_model():
    from app.models import Citizen  # Import the model lazily to avoid circular imports
    if Citizen is None:
        raise RuntimeError("Citizen model not initialized. Ensure `initialize_models` has been called.")
    return Citizen

# GET /api/v1/citizens - List all citizens
@citizens_bp.route('/', methods=['GET'])
def list_citizens():
    Citizen = get_citizen_model()
    citizens = Citizen.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "email": c.email, "constituency": c.constituency}
        for c in citizens
    ]), 200

# POST /api/v1/citizens - Create a new citizen
@citizens_bp.route('/', methods=['POST'])
def create_citizen():
    Citizen = get_citizen_model()
    data = request.json

    # Validate incoming data
    if not all(key in data for key in ['name', 'email', 'constituency']):
        return jsonify({"error": "Missing required fields: name, email, or constituency"}), 400

    new_citizen = Citizen(
        name=data['name'], 
        email=data['email'], 
        constituency=data['constituency']
    )
    db.session.add(new_citizen)
    db.session.commit()
    return jsonify({
        "message": "Citizen created successfully",
        "citizen": {
            "id": new_citizen.id,
            "name": new_citizen.name,
            "email": new_citizen.email,
            "constituency": new_citizen.constituency
        }
    }), 201

# GET /api/v1/citizens/<id> - Retrieve a specific citizen
@citizens_bp.route('/<int:id>', methods=['GET'])
def get_citizen(id):
    Citizen = get_citizen_model()
    citizen = Citizen.query.get_or_404(id)
    return jsonify({
        "id": citizen.id,
        "name": citizen.name,
        "email": citizen.email,
        "constituency": citizen.constituency
    }), 200

# PUT /api/v1/citizens/<id> - Update a specific citizen
@citizens_bp.route('/<int:id>', methods=['PUT'])
def update_citizen(id):
    Citizen = get_citizen_model()
    citizen = Citizen.query.get_or_404(id)
    data = request.json

    # Update fields if provided
    citizen.name = data.get('name', citizen.name)
    citizen.email = data.get('email', citizen.email)
    citizen.constituency = data.get('constituency', citizen.constituency)

    db.session.commit()
    return jsonify({
        "message": "Citizen updated successfully",
        "citizen": {
            "id": citizen.id,
            "name": citizen.name,
            "email": citizen.email,
            "constituency": citizen.constituency
        }
    }), 200

# DELETE /api/v1/citizens/<id> - Delete a citizen
@citizens_bp.route('/<int:id>', methods=['DELETE'])
def delete_citizen(id):
    Citizen = get_citizen_model()
    citizen = Citizen.query.get_or_404(id)
    db.session.delete(citizen)
    db.session.commit()
    return jsonify({"message": "Citizen deleted successfully"}), 200
