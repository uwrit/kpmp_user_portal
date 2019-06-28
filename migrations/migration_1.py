''' script to load mongodb with existing data '''
from pymongo import MongoClient
from pymongo.database import Database
from os import path, environ
import json
from typing import *
import logging
import sys

logging.basicConfig(
    level=logging.INFO if environ.get(
        'ENV') != 'development' else logging.DEBUG,
    format="%(message)s",
    stream=sys.stdout,
)

log = logging.getLogger('migration_1')

def get_mongo():
    cfg_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'config.json')
    if not path.exists(cfg_path):
        raise EnvironmentError('{} file is missing.'.format(cfg_path))
    with open(cfg_path, 'r') as c:
        config = json.load(c)
        if not config.get('MONGO_URI'):
            raise EnvironmentError('Database connection string is missing.')
    return MongoClient(config.get('MONGO_URI')).get_default_database()

def activate_users(mongo: Database):
    mongo.users.update_many(
        {},
        {'$set': {'active': True}}
    )

if __name__ == "__main__":
    mongo = get_mongo()
    log.info('activating users')
    activate_users(mongo)
    log.info('done')
