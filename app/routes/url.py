import string
import random
from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from peewee import fn

from app.models.url import URL

url_bp = Blueprint("url", __name__)

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    for _ in range(10): # try to generate unique code 10 times
        code = ''.join(random.choice(characters) for _ in range(length))
        if not URL.select().where(URL.short_code == code).exists():
            return code
    raise Exception("Failed to generate a unique short code.")

@url_bp.route("/urls", methods=["GET"])
def list_urls():
    urls = URL.select()
    return jsonify([model_to_dict(u) for u in urls])

@url_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()
    if not data or not data.get("original_url"):
        return jsonify({"error": "original_url is required"}), 400
    
    original_url = data["original_url"]
    user_id = data.get("user_id", 1) # Default to 1 if not provided
    title = data.get("title", "")
    
    try:
        short_code = generate_short_code()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    max_id = URL.select(fn.MAX(URL.id)).scalar() or 0
    new_id = max_id + 1
        
    new_url = URL.create(
        id=new_id,
        user_id=user_id,
        short_code=short_code,
        original_url=original_url,
        title=title,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return jsonify(model_to_dict(new_url)), 201
