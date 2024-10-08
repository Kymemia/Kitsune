#!/usr/bin/env python3

"""
Flask app for our platform
"""
from flask import Flask

app = Flask(__name__)

@app.route('/', strict_slashes=False)
def index():
    return 'Welcome to Gig City'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

