import csv
import io
from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from peewee import fn

from app.models.user import User

user_bp = Blueprint("user", __name__)

@user_bp.route("/users", methods=["GET"])
def list_users():
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)
    
    query = User.select()
    
    if page and per_page:
        query = query.paginate(page, per_page)
    
    users = [model_to_dict(u) for u in query]
    return jsonify(users)

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

@user_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    
    user.save()
    return jsonify(model_to_dict(user))

@user_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        user = User.get(User.id == user_id)
    except User.DoesNotExist:
        return jsonify({"error": "User not found"}), 404
    
    user.delete_instance()
    return jsonify({"message": "User deleted"}), 200

@user_bp.route("/users/bulk", methods=["POST"])
def bulk_upload_users():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    
    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)
        
        created = 0
        for row in reader:
            max_id = User.select(fn.MAX(User.id)).scalar() or 0
            User.create(
                id=max_id + 1,
                username=row.get("username", ""),
                email=row.get("email", ""),
                created_at=datetime.utcnow()
            )
            created += 1
        
        return jsonify({"message": f"{created} users created", "count": created}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400