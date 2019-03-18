import os
from flask import request, jsonify, g
from modules.app import mongo
from modules.app.api import api
import modules.logger as logger
from flask_pymongo import ObjectId

LOG = logger.get_root_logger(__name__)


@api.route('/api/org', methods=['GET'])
def get_orgs():
    query = request.args
    orgs = [o for o in mongo.db.orgs.find(query)]
    return jsonify(orgs), 200


@api.route('/api/org/<string:id>', methods=['GET'])
def get_org(id):
    org = mongo.db.orgs.find_one({'_id': ObjectId(id)})
    if not org:
        return jsonify(), 404
    return jsonify(org), 200
