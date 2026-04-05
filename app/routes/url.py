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
    for _ in range(10):
        code = ''.join(random.choice(characters) for _ in range(length))
        if not URL.select().where(URL.short_code == code).exists():
            return code
    raise Exception("Failed to generate a unique short code.")


@url_bp.route("/urls", methods=["GET"])
def list_urls():
    query = URL.select()

    user_id = request.args.get("user_id", type=int)
    if user_id:
        query = query.where(URL.user_id == user_id)

    is_active = request.args.get("is_active")
    if is_active is not None:
        active_val = is_active.lower() in ("true", "1", "yes")
        query = query.where(URL.is_active == active_val)

    short_code = request.args.get("short_code")
    if short_code:
        query = query.where(URL.short_code == short_code)

    title = request.args.get("title")
    if title:
        query = query.where(URL.title.contains(title))

    return jsonify([model_to_dict(u) for u in query])


@url_bp.route("/urls/<int:url_id>", methods=["GET"])
def get_url(url_id):
    try:
        url = URL.get(URL.id == url_id)
        return jsonify(model_to_dict(url))
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404


@url_bp.route("/urls/<int:url_id>/stats", methods=["GET"])
def get_url_stats(url_id):
    try:
        url = URL.get(URL.id == url_id)
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

    from app.models.event import Event
    click_count = Event.select().where(
        (Event.url_id == url_id) & (Event.event_type == "click")
    ).count()

    total_events = Event.select().where(Event.url_id == url_id).count()

    result = model_to_dict(url)
    result["click_count"] = click_count
    result["total_events"] = total_events

    return jsonify(result)


@url_bp.route("/urls", methods=["POST"])
def create_url():
    data = request.get_json()
    if not data or not data.get("original_url"):
        return jsonify({"error": "original_url is required"}), 400

    original_url = data["original_url"]

    # URL format validation
    if not isinstance(original_url, str) or not (
        original_url.startswith("http://") or original_url.startswith("https://")
    ):
        return jsonify({"error": "original_url must start with http:// or https://"}), 400

    user_id = data.get("user_id", 1)
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

    response = jsonify(model_to_dict(new_url))
    response.status_code = 201
    response.headers["Location"] = f"/{new_url.short_code}"
    return response


@url_bp.route("/urls/<int:url_id>", methods=["PUT", "PATCH"])
def update_url(url_id):
    try:
        url = URL.get(URL.id == url_id)
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "title" in data:
        url.title = data["title"]
    if "original_url" in data:
        url.original_url = data["original_url"]
    if "is_active" in data:
        url.is_active = data["is_active"]

    url.updated_at = datetime.utcnow()
    url.save()
    return jsonify(model_to_dict(url))


@url_bp.route("/urls/<int:url_id>", methods=["DELETE"])
def delete_url(url_id):
    try:
        url = URL.get(URL.id == url_id)
    except URL.DoesNotExist:
        return jsonify({"error": "URL not found"}), 404

    url.delete_instance()
    return jsonify({"message": "URL deleted"}), 200
