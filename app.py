#   IMPORT THE NEEDED MODULES
import hmac

from utilities import Utilities
from database_connection import Database

from flask_cors import CORS
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity


class User:
    def __init__(self, bio, user_id, gender, password, username, fullname, phone_number, email_address):
        self.bio = bio
        self.id = user_id
        self.gender = gender
        self.password = password
        self.username = username
        self.fullname = fullname
        self.phone_number = phone_number
        self.email_address = email_address


#   FUNCTION WILL GET USERS FROM THE DATABASE AND CREATE USER OBJECTS
def fetch_users():
    users_array = []
    #   GET USERS FROM THE DATABASE
    db_users = database.get_users()

    #   LOOP THROUGH THE db_users
    for user in db_users:
        #   CREATE A NEW User OBJECT
        users_array.append(User(user[0], user[1], user[2], user[3], user[4], user[5], user[6]))

    #   RETURN THE users_array
    return users_array


#   LOGS IN THE USER AND RETURNS THE USER OBJECT. JWT ALSO USES THIS TO CREATE A JWT TOKEN
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


#   THIS FUNCTION IS USED ON ALL THE ROUTES THAT NEED THE JWT TOKEN. JWT DECODES THE TOKEN AND GETS THE USER DETAILS
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True

app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=86400)

#   INITIALISE THE EXTENSIONS WITH RELEVANT PARAMETERS
CORS(app)
utilities = Utilities()
database = Database("only_frendz.db")
jwt = JWT(app, authenticate, identity)

#   CREATE THE USER TABLE IF IT DOESNT EXIST
print(database.create_user_table())
#   CREATE THE POST TABLE IF IT DOESNT EXIST
print(database.create_post_table())
#   CREATE THE COMMENT TABLE IF IT DOESNT EXIST
print(database.create_comment_table())
#   GET ALL THE USERS IN THE DATABASE
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity

