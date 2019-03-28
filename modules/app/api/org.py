import os
from flask import request, jsonify, g
from modules.app import mongo
from modules.app.api import api
from flask_pymongo import ObjectId
from modules.logger import log


@api.route('/api/org', methods=['GET'])
def get_orgs():
    query = request.args
    log.info("search orgs", query=query, client=g.user['_id'])
    orgs = [o for o in mongo.db.orgs.find(
        query, {'last_changed_by': 0, 'last_changed_on': 0})]
    return jsonify(orgs), 200


@api.route('/api/org/<string:id>', methods=['GET'])
def get_org(id):
    log.info("get org", id=id, client=g.user['_id'])
    org = mongo.db.orgs.find_one({'_id': ObjectId(id)}, {
                                 'last_changed_by': 0, 'last_changed_on': 0})
    if not org:
        return jsonify(), 404
    return jsonify(org), 200
