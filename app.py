import os
import logging
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS for API endpoints
CORS(app)

# Initialize database
from database import init_db
init_db()

# Import routes
from routes import *
