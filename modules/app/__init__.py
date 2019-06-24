''' bootstrap Flask app with MongoDB '''
from flask import Flask, request, jsonify, redirect
import json
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
import datetime
from os import path


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

_config_file = path.join(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))), 'config.json')

app.config.from_json(_config_file)
app.secret_key = app.config['SECRET_KEY']
app.config['DEBUG'] = app.config['ENV'] == 'development'
app.json_encoder = JSONEncoder

@app.route('/', methods=['GET'])
def index():
    return redirect('/admin')

mongo = PyMongo(app)

from modules.app.api import api
app.register_blueprint(api)

from modules.app.admin import admin
