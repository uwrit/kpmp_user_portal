import os
from collections import namedtuple

Config = namedtuple('Config', ['env', 'mongo_uri', 'secret_key'])

_env = os.environ.get('ENV')
if _env and _env == 'development':
    _secret = os.environ.get('SECRET_KEY')
    if not _secret:
        raise EnvironmentError('Missing secret key.')

    _db = os.environ.get('DB')
    if not _db:
        raise EnvironmentError('Missing mongodb connection.')
    config = Config(env=_env, mongo_uri=_db, secret_key=_secret)
else:
    from .config import ENV, MONGO_URI, SECRET_KEY
    config = Config(env=ENV, mongo_uri=MONGO_URI, secret_key=SECRET_KEY)
