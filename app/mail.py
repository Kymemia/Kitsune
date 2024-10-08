#!/usr/bin/env python3

"""
Flask-Mail configuration for sending emails to users
"""
import os
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail

app = Flask(__name__)

app.config['MAIL_SERVER'] = 'stmp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'kistune@gmail.com'

mail = Mail(app)
