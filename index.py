''' index file for Flask API '''
from modules.app import app
import os

if __name__ == "__main__":
    app.config['ENV'] = os.environ.get('ENV')
    app.config['DEBUG'] = os.environ.get('ENV') == 'development'
    app.run(host="0.0.0.0", port=5001)
