#   IMPORT THE NEEDED MODULES
import os
import hmac
import pathlib
import requests
import cloudinary
import cloudinary.uploader
import google.auth.transport.requests

from utilities import Utilities
from database_connection import Database

from flask_mail import Mail
from google.oauth2 import id_token
from datetime import timedelta, date
from pip._vendor import cachecontrol
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
from google_auth_oauthlib.flow import Flow
from flask_jwt import JWT, jwt_required, current_identity
from flask import Flask, jsonify, session, abort, request, redirect, make_response


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
        users_array.append(
            User(user["bio"], user["id"], user["gender"], user["password"], user["username"], user["fullname"],
                 user["phone_number"], user["email_address"]))

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

#   CONFIGURATIONS FOR THE MAIL AND APP TO WORK
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['SECRET_KEY'] = "super-secret"
app.config['MAIL_PASSWORD'] = "!@mBvtmvn"
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['MAIL_USERNAME'] = "notbrucewayne71@gmail.com"
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=86400)

#   INITIALISE THE EXTENSIONS WITH RELEVANT PARAMETERS
CORS(app)
mail = Mail(app)
utilities = Utilities()
socket_io = SocketIO(app)
database = Database("only_frendz.db")
jwt = JWT(app, authenticate, identity)

#   CREATE THE USER TABLE IF IT DOESNT EXIST
print(database.create_user_table())
#   CREATE THE POST TABLE IF IT DOESNT EXIST
print(database.create_post_table())
#   CREATE THE COMMENT TABLE IF IT DOESNT EXIST
print(database.create_comment_table())
#   CREATE THE COMMENT TABLE IF IT DOESNT EXIST
print(database.create_friendship_table())
#   CREATE THE COMMENT TABLE IF IT DOESNT EXIST
print(database.create_like_table())

#   GET ALL THE USERS IN THE DATABASE
users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

# CONFIGURE cloudinary
CLOUDINARY_URL = "cloudinary://423241384786932:ZPBD935sPztWSryQvv_QIFGNOP4@dh3wphqx6"
cloudinary.config(cloud_name='dh3wphqx6',
                  api_key='423241384786932',
                  api_secret='ZPBD935sPztWSryQvv_QIFGNOP4')


# FILE UPLOAD ==========================================================================================================
@app.route("/upload", methods=['POST'])
@cross_origin()
def upload_file():
    app.logger.info('in upload route')

    cloudinary.config(
        cloud_name='dh3wphqx6',
        api_key='423241384786932',
        api_secret='ZPBD935sPztWSryQvv_QIFGNOP4'
    )
    upload_result = None
    if request.method == 'POST':
        file_to_upload = request.files['file']
        app.logger.info('%s file_to_upload', file_to_upload)
        if file_to_upload:
            upload_result = cloudinary.uploader.upload(file_to_upload)
            app.logger.info(upload_result)

            return jsonify(upload_result)


# CUSTOM DECORATOR TO PROTECT SELECTED PAGES FROM UNAUTHORISED USERS BY TAKING IN A FUNCTION AS A PARAMETER
def auth_required(function):
    def wrapper(*args, **kwargs):
        # CHECK IF google_id EXIST IS NOT IN LOCAL SESSION, THEN USER IS UNAUTHORISED
        if "google_id" not in session:
            return abort(401)
        # IF google_id EXIST THEN RETURN THE PASSED IN function
        else:
            return function()

    return wrapper


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# GOOGLE CONSENT SCREEN ================================================================================================
# SAVE THE CLIENT ID FOR LATER USE
GOOGLE_CLIENT_ID = "426022957570-sfmofrh92038d3d352t23c2sggj9v381.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

# THE flow HOLDS INFORMATION ABOUT HOW WE WANT TO AUTHORISE THE USER
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid"
    ],
    redirect_uri="https://only-frendz.herokuapp.com/callback"
)


# ROUTE WILL RECEIVE THE DATA FROM THE GOOGLE ENDPOINT
@app.route("/callback")
def callback():
    # CREATES AN ACCESS TOKEN WITH THE URL PARAMETERS RECEIVED FROM THE GOOGLE CONSENT SCREEN
    flow.fetch_token(authorization_response=request.url)

    # CHECK IF SAVED state MATCHES RECEIVED state
    if not session["state"] == request.args["state"]:
        abort(500)

    # GET AND SAVE THE credentials
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    # SAVE THE id_info
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("https://only-frendz.netlify.app/home")


# LOGIN ROUTE WILL REDIRECT THE USER TO THE GOOGLE LOGIN SCREEN
@app.route("/login/")
def login():
    # authorization_url RETURNS AN AUTHORISATION URL AND THE STATE OF THE FLOW
    authorization_url, state = flow.authorization_url()
    # THE state IS AN OAUTH SECURITY FEATURE SENT BACK FROM AUTHORISATION SERVER
    session["state"] = state
    print(session["state"])
    # REDIRECTS USER TO authorization_url
    return redirect(authorization_url)


# LOGOUT ROUTE WILL CLEAR USER DATA FROM LOCAL SESSION
@app.route("/logout/")
def logout():
    # CLEAR THE USERS SESSION
    session.clear()
    return redirect("/")


# USER ROUTES ==========================================================================================================
#   ROUTE WILL BE USED TO REGISTER A NEW USER, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/user-registration/', methods=["POST"])
def register():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    try:
        #   MAKE SURE THE request.method IS A POST
        if request.method == "POST":
            #   GET THE FORM DATA TO BE SAVED
            username = request.json['username']
            password = request.json['password']
            email_address = request.json['email_address']

            #   MAKE SURE THAT ALL THE ENTRIES ARE VALID
            if utilities.not_empty(username) and utilities.not_empty(password) and utilities.not_empty(
                    email_address) and utilities.is_email(email_address):
                #   CALL THE get_user FUNCTION TO GET THE user
                user = database.get_user(username, password)

                #   IF user EXISTS, THEN LOG THE IN
                if user:
                    response["status_code"] = 409
                    response["message"] = "user already exists"
                    response["email_status"] = "email not sent"
                else:
                    #   CALL THE register_user FUNCTION TO REGISTER THE USER
                    database.register_user(password, username, email_address)
                    #   SEND THE USER AN EMAIL INFORMING THEM ABOUT THEIR REGISTRATION
                    subject = "Only Frendz account registration"
                    message = "Congratulations on a successful registration. Lets make some frendz."
                    utilities.send_email(mail, email_address, subject, message)

                    #   UPDATE THE GLOBAL users
                    global users
                    users = fetch_users()

                    #   GET THE NEWLY REGISTERED USER
                    user = database.get_user(username, password)

                    #   UPDATE THE response
                    response["user"] = user
                    response["status_code"] = 201
                    response["message"] = "registration successful"
                    response["email_status"] = "Email was successfully sent"
    except ValueError:
        #   UPDATE THE response
        response["status_code"] = 409
        response["current_user"] = "none"
        response["message"] = "inputs are not valid"
        response["email_status"] = "email not sent"
    finally:
        #   RETURN THE response
        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route('/users/', methods=["GET"])
def get_users():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   GET THE NEWLY REGISTERED USER
    db_users = database.get_users()

    #   UPDATE THE response
    response["users"] = db_users
    response["status_code"] = 201
    response["message"] = "users successfully retrieved"

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#   ROUTE WILL BE USED TO REGISTER A NEW USER, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/user-update/<int:user_id>/', methods=["PUT"])
# @jwt_required()
def update_user(user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    try:
        #   MAKE SURE THE request.method IS A POST
        if request.method == "PUT":
            #   GET THE FORM DATA TO BE SAVED
            bio = request.json['bio']
            username = request.json['username']
            fullname = request.json['fullname']
            password = request.json['new_password']
            profile_img = request.json['profile_img']
            phone_number = request.json['phone_number']
            email_address = request.json['email_address']

            #   MAKE SURE THAT ALL THE ENTRIES ARE VALID
            if utilities.not_empty(username) and utilities.not_empty(password) and utilities.not_empty(email_address) \
                    and utilities.not_empty(fullname) and utilities.not_empty(profile_img) \
                    and utilities.not_empty(phone_number) and utilities.is_email(email_address):
                #   CALL THE get_user FUNCTION TO GET THE user
                database.update_user(user_id, bio, password, username, fullname, phone_number, email_address)
                #   UPDATE THE response
                response["status_code"] = 201
                response["message"] = "update successful"
    except ValueError:
        #   UPDATE THE response
        response["status_code"] = 409
        response["message"] = "something went wrong"
        response["email_status"] = "email not sent"
    finally:
        #   RETURN THE response
        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route("/user/<int:user_id>/", methods=["GET"])
def get_user(user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    try:
        #   MAKE SURE THE request.method IS A POST
        if request.method == "GET":
            user = database.get_user_by_id(user_id)

            #   IF THE USER EXISTS, ADD IT TO THE RESPONSE
            if user:
                response['user'] = user
                response['status_code'] = 201
                response['message'] = 'User retrieved successfully'
            else:
                response['user'] = 'none'
                response['status_code'] = 409
                response['message'] = 'User not found'
    except ValueError:
        #   UPDATE THE response
        response["status_code"] = 409
        response['message'] = 'something went wrong'
    finally:
        #   RETURN THE response
        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


#   ROUTE WILL BE USED TO LOG A REGISTERED USER IN, ROUTE ONLY ACCEPTS A POST METHOD
@app.route("/delete-user/<int:user_id>/", methods=["GET"])
def delete_user(user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    try:
        #   MAKE SURE THE request.method IS A POST
        if request.method == "GET":
            if database.delete_user(user_id) == "user deleted":
                response['status_code'] = 201
                response['message'] = 'User deleted successfully'
            else:
                response['status_code'] = 409
                response['message'] = 'User not deleted'
    except ValueError:
        #   UPDATE THE response
        response["status_code"] = 409
        response['message'] = 'User not deleted'
    finally:
        #   RETURN THE response
        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


# POST ROUTES ==========================================================================================================
#   ROUTE WILL BE USED TO ADD A NEW PRODUCT, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/create-post/', methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def add_post():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A POST
    if request.method == "POST":
        try:
            today = date.today()

            #   GET THE FORM DATA TO BE SAVED
            post = request.json['post']
            image_url = request.json['image_url']
            user_id = request.json['user_id']
            date_created = today.strftime("%B %d, %Y")

            #   CALL THE save_product FUNCTION TO SAVE THE PRODUCT TO THE DATABASE
            database.create_post(user_id, post, image_url, date_created)

            #   UPDATE THE response
            response["status_code"] = 201
            response['message'] = "post successfully added"
        except ValueError:
            #   UPDATE THE response
            response["status_code"] = 409
            response['message'] = "inputs are not valid"
        finally:
            #   RETURN THE response
            response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


#   ROUTE WILL BE USED TO ADD A NEW PRODUCT, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/update-post/<int:post_id>/', methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def update_post(post_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A POST
    if request.method == "POST":
        try:
            #   GET THE FORM DATA TO BE SAVED
            post = request.json['post']
            image_url = request.json['image_url']

            #   CALL THE save_product FUNCTION TO SAVE THE PRODUCT TO THE DATABASE
            database.update_post(post_id, post, image_url)

            #   UPDATE THE response
            response["status_code"] = 201
            response['message'] = "post successfully updated"
        except ValueError:
            #   UPDATE THE response
            response["status_code"] = 409
            response['message'] = "something went wrong"
        finally:
            #   RETURN THE response
            response = make_response(response)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response


#   ROUTE WILL BE USED TO VIEW ALL PRODUCTS, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-posts/', methods=["GET"])
# @jwt_required()
def get_posts():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A GET
    if request.method == "GET":
        #   GET ALL THE PRODUCTS FROM THE DATABASE
        posts = database.get_posts()

        if len(posts) > 0:
            #   UPDATE THE response
            response['status_code'] = 201
            response['posts'] = posts
            response["message"] = "posts retrieved successfully"

        else:
            #   UPDATE THE response
            response['status_code'] = 409
            response['posts'] = "none"
            response['message'] = "there are no posts in the database"

    #   RETURN THE response
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#   ROUTE WILL BE USED TO VIEW ALL PRODUCTS, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-posts/<int:user_id>/', methods=["GET"])
# @jwt_required()
def get_users_posts(user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A GET
    if request.method == "GET":
        #   GET ALL THE PRODUCTS FROM THE DATABASE
        posts = database.get_user_posts(user_id)

        if len(posts) > 0:
            #   UPDATE THE response
            response['status_code'] = 201
            response['posts'] = posts
            response["message"] = "posts retrieved successfully"

        else:
            #   UPDATE THE response
            response['status_code'] = 409
            response['posts'] = "none"
            response['message'] = "there are no posts in the database"

    #   RETURN THE response
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#   ROUTE WILL BE USED TO VIEW A SINGLE PRODUCT, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-post/<int:post_id>/', methods=["GET"])
# @jwt_required()
def get_post(post_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A GET
    if request.method == "GET":
        #   GET A PRODUCT FROM THE DATABASE
        post = database.get_post(post_id)

        if post:
            #   UPDATE THE response
            response["status_code"] = 201
            response["post"] = post
            response["message"] = "post retrieved successfully"
        else:
            #   UPDATE THE response
            response["status_code"] = 409
            response["post"] = "none"
            response["message"] = "post not found"

    #   RETURN THE response
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/delete-post/<int:post_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def delete_post(post_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    database.delete_post(post_id)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "post deleted successfully."

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# COMMENT ROUTES =======================================================================================================
#   ROUTE WILL BE USED TO ADD A NEW PRODUCT, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/create-comment/<int:post_id>/<int:user_id>/', methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def add_comment(post_id, user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A POST
    if request.method == "POST":
        today = date.today()
        #   GET THE FORM DATA TO BE SAVED
        comment = request.json['comment']
        date_created = today.strftime("%B %d, %Y")

        #   CALL THE save_product FUNCTION TO SAVE THE PRODUCT TO THE DATABASE
        database.create_comment(user_id, comment, post_id, date_created)

        #   UPDATE THE response
        response["status_code"] = 201
        response['message'] = "comment successfully added"

    #   RETURN THE response
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


#   ROUTE WILL BE USED TO VIEW ALL PRODUCTS, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-comments/', methods=["GET"])
# @jwt_required()
def get_comments():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A GET
    if request.method == "GET":
        #   GET ALL THE PRODUCTS FROM THE DATABASE
        comments = database.get_comments()

        if len(comments) > 0:
            #   UPDATE THE response
            response['status_code'] = 201
            response['comments'] = comments
            response["message"] = "comments retrieved successfully"

        else:
            #   UPDATE THE response
            response['status_code'] = 409
            response['comments'] = "none"
            response['message'] = "there are no comments in the database"

    #   RETURN THE response
    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/delete-comment/<int:comment_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def delete_comment(comment_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    database.delete_comment(comment_id)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "comment deleted successfully."

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# FRIENDSHIP ROUTES ====================================================================================================
@app.route("/make-friendship/<int:user_id>/<int:friend_id>/", methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def make_friendship(user_id, friend_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    today = date.today()
    date_started = today.strftime("%B %d, %Y")

    #   CALL THE delete_product AND PASS IN THE product_id
    database.create_friendship(user_id, friend_id, date_started)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "friendship started"

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/get-friends/<int:user_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def get_friends(user_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    friends = database.get_friends(user_id)

    if friends:
        #   UPDATE THE response
        response["status_code"] = 201
        response["friends"] = friends
        response["message"] = "friends retrieved successfully"
    else:
        #   UPDATE THE response
        response["status_code"] = 409
        response["friends"] = "none"
        response["message"] = "friends not found"

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/end-friendship/<int:user_id>/<int:friend_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
# @jwt_required()
def end_friendship(user_id, friend_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    database.end_friendship(user_id, friend_id)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "friendship ended"

    response = make_response(response)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


# LIKE ROUTES ==========================================================================================================
@app.route("/get-likes/", methods=["GET"])
def get_likes():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    if request.method == "GET":
        #   CALL THE delete_product AND PASS IN THE product_id
        likes = database.get_likes()

        #   UPDATE THE response
        response["likes"] = likes
        response['status_code'] = 201
        response["message"] = "likes retrieved successfully"

        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


@app.route("/add-like/<int:user_id>/<int:post_id>/", methods=["POST"])
def add_like(user_id, post_id):
    response = {}

    if request.method == "POST":
        database.add_like(user_id, post_id)

        #   UPDATE THE response
        response['status_code'] = 201
        response['message'] = "like added"

        response = make_response(response)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response


# SOCKET IO ROUTES =====================================================================================================
@socket_io.on("broadcast message")
def message_display(data):
    emit("show message", {"message": data["message"]}, broadcast=True)


if __name__ == "__main__":
    socket_io.run(app)
