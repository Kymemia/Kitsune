#!/usr/bin/env python3

from flask import Flask
from routes.pesapal_service import pesapal_blueprint

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.register_blueprint(pesapal_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
