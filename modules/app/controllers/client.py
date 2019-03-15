import os
from flask import request, jsonify
from modules.app import app, mongo
import modules.logger as logger

LOG = logger.get_root_logger(__name__)


@app.route('/api/user', methods=['GET'])
def get():
    token = str(request.headers.get('X-API-TOKEN'))
    if not token:
        return jsonify({'ok': False, 'message': 'Unauthenticated.'}), 403
    client = mongo.db.apps.find_one({'token': token.encode('utf-8', 'strict')})
    if not client:
        return jsonify({'ok': False, 'message': 'Invalid API Token'}), 403
    LOG.info({'_id': client['_id'], 'client': client['name']})
    query = request.args
    users = [u for u in mongo.db.users.find(query)]
    return jsonify(users), 200


@app.route('/api/user', methods=['POST'])
def post():
    return "", 200
