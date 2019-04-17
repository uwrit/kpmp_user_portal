''' index file for Flask API '''
from modules import logger
from modules.app import app
import os

PORT = os.environ.get('PORT')
if PORT:
    PORT = int(PORT)
else:
    PORT = 5001

if __name__ == "__main__":
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    host = '0.0.0.0' if app.config['DEBUG'] else None
    app.run(host=host, port=PORT)
