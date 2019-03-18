''' all api controllers '''
import os
import glob
from flask import Blueprint, request, g, jsonify
from modules.app import mongo, api

api = Blueprint('api', __name__)


@api.before_request
def authenticated():
    token = str(request.headers.get('X-API-TOKEN'))
    if not token:
        return jsonify({'ok': False, 'message': 'Unauthenticated.'}), 403
    client = mongo.db.clients.find_one(
        {'token': token})
    if not client:
        return jsonify({'ok': False, 'message': 'Unauthenticated.'}), 403
    g.user = client


from .user import get_users, get_user
from .org import get_orgs, get_org
