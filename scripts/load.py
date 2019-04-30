''' script to load mongodb with existing data '''
from modules.envi import env
from pymongo import MongoClient
from os import path
import json
from typing import *
import logging
import sys

logging.basicConfig(
    level=logging.INFO if env.get(
        'ENV') != 'development' else logging.DEBUG,
    format="%(message)s",
    stream=sys.stdout,
)

log = logging.getLogger('loader')

DATA_DIRECTORY = path.join(path.dirname(
    path.dirname(path.abspath(__file__))), 'data')

USER_FILE = path.join(DATA_DIRECTORY, 'user-profiles-export.json')
ORG_FILE = path.join(DATA_DIRECTORY, 'orgs-export.json')


def read_json_file(path: str) -> Any:
    with open(path, 'r') as f:
        return json.load(f)


class Cache:
    def __init__(self, users, orgs):
        self.users: dict = users
        self.orgs: dict = orgs

    def remap_user_orgs(self):
        for u in self.users.values():
            if u.get('org_code'):
                org = self.orgs.get(u['org_code'])
                if org:
                    u['organization_id'] = str(org['_id'])
                del u['org_code']


class KPMPMongoLoader:
    def __init__(self, mongo):
        self.db = mongo

    def load_orgs(self, orgs: dict):
        result = self.db.orgs.insert_many(orgs.values())
        log.info(f'Inserted {len(result.inserted_ids)} orgs...')
        return [o for o in self.db.orgs.find()]

    def load_users(self, users: dict):
        result = self.db.users.insert_many(users.values())
        log.info(f'Inserted {len(result.inserted_ids)} users...')
        return [u for u in self.db.users.find()]


def get_mongo():
    cstr = env.get('DB')
    if not cstr:
        raise EnvironmentError('Database connection string is missing.')
    return MongoClient(env.get('DB')).get_default_database()


def cache_data():
    users = {u['shib_id']: u for u in read_json_file(USER_FILE)}
    orgs = {o['code']: o for o in read_json_file(ORG_FILE)}
    return Cache(users, orgs)


if __name__ == "__main__":
    log.info('Loading KPMP User Portal MongoDB...')
    cache = cache_data()
    loader = KPMPMongoLoader(get_mongo())
    cache.orgs = {o['code']: o for o in loader.load_orgs(cache.orgs)}
    cache.remap_user_orgs()
    cache.users = {u['shib_id']: u for u in loader.load_users(cache.users)}
    log.info('Done.')
