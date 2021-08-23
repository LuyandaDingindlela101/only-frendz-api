#   IMPORT THE NEEDED MODULES
import hmac

# from utilities import Utilities
from database_connection import Database

from flask_cors import CORS
from datetime import timedelta
from flask_mail import Mail, Message
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity

app = Flask(__name__)
app.debug = True