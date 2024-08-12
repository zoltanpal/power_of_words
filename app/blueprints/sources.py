from flask import Blueprint, jsonify

from app.models.sources import Sources
from libs.database import db

sources_bp = Blueprint("sources", __name__, url_prefix="/sources")


@sources_bp.route("/get_all")
def get_data():
    # Create a session within the application context
    with db.session() as session:
        # Perform SELECT query
        result = session.query(Sources).all()

        # Convert the result to a dictionary for JSON response
        data = [{"id": record.id, "name": record.name} for record in result]

    return jsonify(data)
