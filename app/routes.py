from flask import Blueprint, render_template, request, jsonify, abort
from app.services import fetch_ispark_data, get_parking_within_radius, get_drive_info

main = Blueprint("main", __name__)

@main.route("/", methods=["GET"])
def map():
    ispark_data = fetch_ispark_data()
    return render_template("index.html", ispark_data=ispark_data)


@main.route("/api/ispark-data", methods=["GET"])
def fetch_ispark_data_api():
    try:
        ispark_data = fetch_ispark_data()
        return jsonify({"data": ispark_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main.route("/api/nearest-parking", methods=["POST"])
def get_parking_nearby():
    try:
        data = request.json
        user_lat = float(data.get("lat"))
        user_lng = float(data.get("lng"))

        parking_lots = get_parking_within_radius(user_lat, user_lng, radius=10, limit=30)

        return jsonify({"data": parking_lots})

    except Exception as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400


@main.route("/api/drive-info", methods=["POST"])
def get_nav_info():
    try:
        data = request.json
        user_lat = float(data.get("lat"))
        user_lng = float(data.get("lng"))
        parking_lots = data.get("parkingLots")

        enriched_lots = get_drive_info(user_lat, user_lng, parking_lots)

        return jsonify({"enriched_parking_lots": enriched_lots})

    except Exception as e:
        return jsonify({"error": f"Invalid request: {str(e)}"}), 400
