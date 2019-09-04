from flask import Blueprint, request, jsonify

from .tasks import process_job

api = Blueprint('api', 'api', url_prefix='/api')

@api.route('/safety_score', methods=['GET'])
def generate_safety_score():
    mac = request.args.get('mac', default = None, type = str)
    if mac is None:
        return jsonify({'error': 'Mac address is required'}), 422
    print('received')
    process_job.send(mac)
    return jsonify({'status': 'processed'}), 200


