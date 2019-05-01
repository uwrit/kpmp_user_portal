''' bootstrap Flask app with MongoDB '''
from modules.config import config
from flask import Flask, request, jsonify
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

app = Flask(__name__)

app.secret_key = config.secret_key
app.config['MONGO_URI'] = config.mongo_uri
app.config['ENV'] = config.env
app.config['DEBUG'] = config.env == 'development'
app.json_encoder = JSONEncoder

mongo = PyMongo(app)

from modules.app.api import api
app.register_blueprint(api)

from modules.app.admin import admin
