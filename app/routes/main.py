# app/routes/main.py
from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def homepage():
    return jsonify({"message": "Welcome to the Campaign Management System!"})
