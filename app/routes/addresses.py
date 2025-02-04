from flask import Blueprint, request, jsonify
from app.models.factory import get_model
from app import db

bp = Blueprint('addresses', __name__)  # Changed to bp to match convention

def get_address_model():
    """Helper function to get the Address model"""
    return get_model("Address")

@bp.route("/", methods=["GET"])
def get_addresses():
    """Retrieve all addresses."""
    Address = get_address_model()
    addresses = Address.query.all()
    return jsonify([{
        "id": a.id, 
        "street": a.street, 
        "city": a.city, 
        "state": a.state, 
        "zip_code": a.zip_code
    } for a in addresses])

@bp.route("/", methods=["POST"])
def create_address():
    """Create a new address."""
    Address = get_address_model()
    data = request.get_json()
    new_address = Address(
        street=data["street"],
        city=data["city"],
        state=data["state"],
        zip_code=data["zip_code"]
    )
    db.session.add(new_address)
    db.session.commit()
    return jsonify({"message": "Address created", "id": new_address.id}), 201

@bp.route("/<int:address_id>", methods=["GET"])
def get_address(address_id):
    """Retrieve a specific address by ID."""
    Address = get_address_model()
    address = Address.query.get_or_404(address_id)
    return jsonify({
        "id": address.id, 
        "street": address.street, 
        "city": address.city, 
        "state": address.state, 
        "zip_code": address.zip_code
    })

@bp.route("/<int:address_id>", methods=["PUT"])
def update_address(address_id):
    """Update an existing address."""
    Address = get_address_model()
    address = Address.query.get_or_404(address_id)
    data = request.get_json()
    address.street = data.get("street", address.street)
    address.city = data.get("city", address.city)
    address.state = data.get("state", address.state)
    address.zip_code = data.get("zip_code", address.zip_code)
    db.session.commit()
    return jsonify({"message": "Address updated"})

@bp.route("/<int:address_id>", methods=["DELETE"])
def delete_address(address_id):
    """Delete an address."""
    Address = get_address_model()
    address = Address.query.get_or_404(address_id)
    db.session.delete(address)
    db.session.commit()
    return jsonify({"message": "Address deleted"})