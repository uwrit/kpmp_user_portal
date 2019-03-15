import os
from flask import request, jsonify
from modules.app import app, mongo
import modules.logger as logger


def get_client():
    token = str(request.headers.get('X-API-TOKEN'))
    if not token:
        return {'ok': False, 'message': 'Unauthenticated.'}
    client = mongo.db.apps.find_one({'token': token.encode('utf-8', 'strict')})
    if not client:
        return {'ok': False, 'message': 'Unauthenticated.'}
    return {'ok': True, 'client':
            client}
