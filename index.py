''' index file for Flask API '''
from modules.envi import env
from modules import logger
from modules.app import app

HOST = None
_containerd = env.get('FLASK_RUNNING_IN_DOCKER')
if _containerd and _containerd == 'true':
    HOST = '0.0.0.0'

PORT = env.get('PORT')
if PORT:
    PORT = int(PORT)
else:
    PORT = 5001

if __name__ == "__main__":
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    app.run(host=HOST, port=PORT)
