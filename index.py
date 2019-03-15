''' index file for Flask API '''
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

@app.route('/user', methods=['GET'])
def get():
    users = str([u for u in mongo.db.user.find()])
    print(users)
    return jsonify(users)

if __name__ == "__main__":
    app.config['ENV'] = os.environ.get('ENV')
    app.config['DEBUG'] = os.environ.get('ENV') == 'development'
    app.run(host="0.0.0.0", port=5001)