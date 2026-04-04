from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from peewee import fn

from app.models.user import User

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def list_users():
    users = User.select()
    return jsonify([model_to_dict(p) for p in users])

@user_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.get(User.id == user_id)
        return jsonify(model_to_dict(user))
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404

@user_bp.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "username and email are required"}), 400
        
    # Check if user already exists
    if User.select().where((User.username == data["username"]) | (User.email == data["email"])).exists():
        return jsonify({"error": "User with that username or email already exists"}), 409
        
    max_id = User.select(fn.MAX(User.id)).scalar() or 0
    new_id = max_id + 1
    
    new_user = User.create(
        id=new_id,
        username=data["username"],
        email=data["email"],
        created_at=datetime.utcnow()
    )
    
    return jsonify(model_to_dict(new_user)), 201