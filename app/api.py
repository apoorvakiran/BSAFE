import logging
from flask import Blueprint, request, jsonify

from .tasks import safety_score_analysis, status

api = Blueprint("api", "api", url_prefix="/api")

logger = logging.getLogger()


@api.route("/safety_score", methods=["GET"])
def generate_safety_score():
    mac = request.args.get("mac", default=None, type=str)
    start_time = request.args.get("start_time", default=None, type=str)
    end_time = request.args.get("end_time", default=None, type=str)
    if mac is None or start_time is None or end_time is None:
        return jsonify({"error": "Missing required parameter"}), 422
    logger.info(f"Received mac {mac}")
    safety_score_analysis.send(mac, start_time, end_time)
    return jsonify({"status": "processed"}), 200


@api.route("/status", methods=["GET"])
def generate_status():
    response = status.send()
    response.update(**{"status": "processed"})

    return jsonify(response), int(response["status_code"])
