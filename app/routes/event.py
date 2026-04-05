from datetime import datetime
from flask import Blueprint, jsonify, request
from playhouse.shortcuts import model_to_dict
from peewee import fn

from app.models.event import Event

event_bp = Blueprint("event", __name__)

@event_bp.route("/events", methods=["GET"])
def list_events():
    query = Event.select()
    
    url_id = request.args.get("url_id", type=int)
    if url_id:
        query = query.where(Event.url_id == url_id)
    
    user_id = request.args.get("user_id", type=int)
    if user_id:
        query = query.where(Event.user_id == user_id)
    
    event_type = request.args.get("event_type")
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    return jsonify([model_to_dict(e) for e in query])

@event_bp.route("/events/<int:event_id>", methods=["GET"])
def get_event(event_id):
    try:
        event = Event.get(Event.id == event_id)
        return jsonify(model_to_dict(event))
    except Event.DoesNotExist:
        return jsonify({"error": "Event not found"}), 404

@event_bp.route("/events", methods=["POST"])
def create_event():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    if not data.get("url_id") or not data.get("event_type"):
        return jsonify({"error": "url_id and event_type are required"}), 400
    
    max_id = Event.select(fn.MAX(Event.id)).scalar() or 0
    new_id = max_id + 1
    
    details = data.get("details", "")
    # Handle dict/object details by converting to string
    if isinstance(details, dict):
        import json
        details = json.dumps(details)
    
    new_event = Event.create(
        id=new_id,
        url_id=data["url_id"],
        user_id=data.get("user_id", 0),
        event_type=data["event_type"],
        timestamp=datetime.utcnow(),
        details=details
    )
    
    return jsonify(model_to_dict(new_event)), 201
