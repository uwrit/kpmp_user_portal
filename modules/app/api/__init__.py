''' all api controllers '''
import glob
from flask import Blueprint, request, g, jsonify
from modules.app import mongo, api
from modules.logger import log

api = Blueprint('api', __name__)


@api.before_request
def authenticated():
    token = str(request.headers.get('X-API-TOKEN'))
    if not token:
        log.warning("missing X-API-TOKEN header")
        return jsonify({'ok': False, 'message': 'Unauthenticated.'}), 403
    client = mongo.db.clients.find_one(
        {'token': token})
    if not client:
        log.warning("incorrect API token.", token=token)
        return jsonify({'ok': False, 'message': 'Unauthenticated.'}), 403
    g.user = client


from .user import get_users, get_user
from .org import get_orgs, get_org
