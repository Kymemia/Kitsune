#!/usr/bin/env python3

from flask import Flask
from routes.pesapal_service import pesapal_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(pesapal_blueprint)
    return app
