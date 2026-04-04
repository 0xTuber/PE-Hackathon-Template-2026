from datetime import datetime
from flask import Blueprint, redirect, jsonify, request
from peewee import fn

from app.models.url import URL
from app.models.event import Event

redirect_bp = Blueprint("redirect", __name__)

@redirect_bp.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code):
    try:
        url = URL.get(URL.short_code == short_code)
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404
        
    if not url.is_active:
        return jsonify({"error": "URL is inactive"}), 400
        
    max_event_id = Event.select(fn.MAX(Event.id)).scalar() or 0
    new_event_id = max_event_id + 1

    # Record the click event
    Event.create(
        id=new_event_id,
        url_id=url.id,
        user_id=0, # 0 or null for anonymous visits
        event_type="click",
        timestamp=datetime.utcnow(),
        details=request.user_agent.string
    )
    
    return redirect(url.original_url)
