''' bootstrap Flask app with MongoDB '''
from flask import Flask, request, jsonify
from flask_admin import Admin
import os
import json
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
import datetime


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


_secret = os.environ.get('SECRET_KEY')
if not _secret:
    raise EnvironmentError('Missing secret key.')

_db = os.environ.get('DB')
if not _db:
    raise EnvironmentError('Missing mongodb connection.')

_env = os.environ.get('ENV')
if not _env:
    _env = 'production'


app = Flask(__name__)

app.secret_key = _secret
app.config['MONGO_URI'] = _db
app.config['ENV'] = _env
app.json_encoder = JSONEncoder

mongo = PyMongo(app)

from modules.app.api import api
app.register_blueprint(api)

from modules.app.admin import admin
