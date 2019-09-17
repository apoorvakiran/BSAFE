import logging
from flask import Blueprint, request, jsonify

from .tasks import safety_score_analysis

api = Blueprint('api', 'api', url_prefix='/api')

logger = logging.getLogger()

@api.route('/safety_score', methods=['GET'])
def generate_safety_score():
    mac = request.args.get('mac', default = None, type = str)
    from_date = request.args.get('from_date', default = None, type = str)
    till_date = request.args.get('till_date', default = None, type = str)
    if mac is None or from_date is None or till_date is None:
        return jsonify({'error': 'Missing required parameter'}), 422
    logger.info(f"Received mac {mac}")
    safety_score_analysis.send(mac, from_date, till_date)
    return jsonify({'status': 'processed'}), 200


