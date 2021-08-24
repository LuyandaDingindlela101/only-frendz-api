#   IMPORT THE NEEDED MODULES
import hmac

from utilities import Utilities
from database_connection import Database

from flask_mail import Mail
from flask_cors import CORS
from datetime import timedelta, date
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
        print(user)
        users_array.append(User(user[3], user[0], user[6], user[7], user[3], user[1], user[5], user[4]))

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
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PASSWORD'] = "notBruceWayne"
app.config['MAIL_USERNAME'] = "notbrucewayne71@gmail.com"
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=86400)

#   INITIALISE THE EXTENSIONS WITH RELEVANT PARAMETERS
CORS(app)
mail = Mail(app)
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
                    # utilities.send_email(mail, email_address, username)
                    #   GET THE NEWLY REGISTERED USER
                    user = database.get_user(username, password)

                    global users
                    users = fetch_users()

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
        return response


#   ROUTE WILL BE USED TO LOG A REGISTERED USER IN, ROUTE ONLY ACCEPTS A POST METHOD
@app.route("/user-login/", methods=["POST"])
def login():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A POST
    if request.method == "POST":
        try:
            #   GET THE FORM DATA TO BE SAVED
            username = request.json['username']
            password = request.json['password']

            #   MAKE SURE THAT ALL THE ENTRIES ARE VALID
            if utilities.not_empty(username) and utilities.not_empty(password):
                #   CALL THE get_user FUNCTION TO GET THE user
                user = database.get_user(username, password)

                #   IF user EXISTS, THEN LOG THE IN
                if user:
                    #   UPDATE THE response
                    response["status_code"] = 201
                    response["current_user"] = user
                    response["message"] = "login successful"
                else:
                    #   UPDATE THE response
                    response["status_code"] = 409
                    response["current_user"] = "none"
                    response["message"] = "login unsuccessful"
        except ValueError:
            #   UPDATE THE response
            response["status_code"] = 409
            response["user"] = "none"
            response["message"] = "inputs are not valid"
            response["email_status"] = "email not sent"
        finally:
            #   RETURN THE response
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
                response['status_code'] = 200
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
        return response


#   ROUTE WILL BE USED TO ADD A NEW PRODUCT, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/create-post/', methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
@jwt_required()
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
            return response


#   ROUTE WILL BE USED TO VIEW ALL PRODUCTS, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-posts/', methods=["GET"])
@jwt_required()
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
    return response


#   ROUTE WILL BE USED TO VIEW A SINGLE PRODUCT, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-post/<int:post_id>/', methods=["GET"])
@jwt_required()
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
            response["message"] = "product retrieved successfully"
        else:
            #   UPDATE THE response
            response["status_code"] = 409
            response["post"] = "none"
            response["message"] = "product not found"

    #   RETURN THE response
    return response


@app.route("/delete-post/<int:post_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
@jwt_required()
def delete_post(post_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    database.delete_post(post_id)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "post deleted successfully."

    return response


#   ROUTE WILL BE USED TO ADD A NEW PRODUCT, ROUTE ONLY ACCEPTS A POST METHOD
@app.route('/create-comment/', methods=["POST"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
@jwt_required()
def add_comment():
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   MAKE SURE THE request.method IS A POST
    if request.method == "POST":
        try:
            today = date.today()

            #   GET THE FORM DATA TO BE SAVED
            comment = request.json['comment']
            post_id = request.json['post_id']
            user_id = request.json['user_id']
            date_created = today.strftime("%B %d, %Y")

            #   CALL THE save_product FUNCTION TO SAVE THE PRODUCT TO THE DATABASE
            database.create_comment(user_id, comment, post_id, date_created)

            #   UPDATE THE response
            response["status_code"] = 201
            response['message'] = "comment successfully added"
        except ValueError:
            #   UPDATE THE response
            response["status_code"] = 409
            response['message'] = "inputs are not valid"
        finally:
            #   RETURN THE response
            return response


#   ROUTE WILL BE USED TO VIEW ALL PRODUCTS, ROUTE ONLY ACCEPTS A GET METHOD
@app.route('/get-comments/', methods=["GET"])
@jwt_required()
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
    return response


@app.route("/delete-comment/<int:comment_id>/", methods=["GET"])
#   AN AUTHORISATION TOKEN IS NEEDED TO ACCESS THIS ROUTE
@jwt_required()
def delete_comment(comment_id):
    #   CREATE AN EMPTY OBJECT THAT WILL HOLD THE response OF THE PROCESS
    response = {}

    #   CALL THE delete_product AND PASS IN THE product_id
    database.delete_comment(comment_id)

    #   UPDATE THE response
    response['status_code'] = 201
    response['message'] = "comment deleted successfully."

    return response
