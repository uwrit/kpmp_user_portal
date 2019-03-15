import os
from flask import request, jsonify
from modules.app import app, mongo
import modules.logger as logger
from .utils import get_client

LOG = logger.get_root_logger(__name__)


@app.route('/api/user', methods=['GET'])
def get():
    c = get_client()
    if not c['ok']:
        return jsonify(c), 403
    query = request.args
    users = [u for u in mongo.db.users.find(query)]
    return jsonify(users), 200


@app.route('/api/user', methods=['POST'])
def post():
    return "", 200
