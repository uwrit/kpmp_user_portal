''' bootstrap Flask app with MongoDB '''
from flask import Flask, request, jsonify
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


app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get('DB')
app.json_encoder = JSONEncoder

mongo = PyMongo(app)

from modules.app.api import api
app.register_blueprint(api)
