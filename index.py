''' index file for Flask API '''
from modules import logger
from modules.app import app
import os

HOST = None
_containerd = os.environ.get('FLASK_RUNNING_IN_DOCKER')
if _containerd and _containerd == 'true':
    HOST = '0.0.0.0'

PORT = os.environ.get('PORT')
if PORT:
    PORT = int(PORT)
else:
    PORT = 5001

if __name__ == "__main__":
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    app.run(host=HOST, port=PORT)
