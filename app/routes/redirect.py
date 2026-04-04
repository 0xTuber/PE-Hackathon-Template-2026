from datetime import datetime
from flask import Blueprint, redirect, jsonify, request
from peewee import fn
import redis
import os

from app.models.url import URL
from app.models.event import Event

redirect_bp = Blueprint("redirect", __name__)

# Dynamically route Redis location safely utilizing System Defaults
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

@redirect_bp.route("/<short_code>", methods=["GET"])
def redirect_to_url(short_code):
    # 1. OPTIMIZATION: Check Memory Cache explicitly first
    try:
        cached_url = redis_client.get(f"url:{short_code}")
        if cached_url:
            # Shift heavy DB sync writes entirely to blistering RAM `INCR` commands 
            redis_client.incr(f"clicks:{short_code}")
            
            response = redirect(cached_url)
            # Evidence of Caching (Loot Header)
            response.headers["X-Cache-Status"] = "HIT"
            return response
    except redis.ConnectionError:
        pass # Natively failover to robust DB layer safely if Cache shuts down

    # 2. Database Fallback Read
    try:
        url = URL.get(URL.short_code == short_code)
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404
        
    if not url.is_active:
        return jsonify({"error": "URL is inactive"}), 400
        
    max_event_id = Event.select(fn.MAX(Event.id)).scalar() or 0
    new_event_id = max_event_id + 1

    # Record the strict synchronized DB click natively
    Event.create(
        id=new_event_id,
        url_id=url.id,
        user_id=0, # Anonymous visits
        event_type="click",
        timestamp=datetime.utcnow(),
        details=request.user_agent.string
    )
    
    # 3. Secure output directly back to Redis to bypass the bottleneck perfectly
    try:
        # Cache for exactly one hour securely
        redis_client.setex(f"url:{short_code}", 3600, url.original_url)
    except redis.ConnectionError:
        pass
    
    response = redirect(url.original_url)
    response.headers["X-Cache-Status"] = "MISS"
    return response
