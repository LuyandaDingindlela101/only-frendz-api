import sqlite3
from utilities import Utilities


class Database:
    def __init__(self, database_name):
        self.database_name = database_name
        self.utilities = Utilities()

    # TABLES CREATION ==================================================================================================
    #   FUNCTION WILL CREATE THE USER TABLE
    def create_user_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS user("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "fullname TEXT DEFAULT 'NULL' NOT NULL,"
                               "profile_img TEXT DEFAULT 'NULL' NOT NULL,"
                               "bio TEXT DEFAULT 'NULL' NOT NULL,"
                               "username TEXT NOT NULL,"
                               "email_address TEXT NOT NULL,"
                               "phone_number TEXT DEFAULT 'NULL' NOT NULL,"
                               "gender TEXT DEFAULT 'NULL' NOT NULL,"
                               "password TEXT NOT NULL)")

        return "user table created successfully"

    #   FUNCTION WILL CREATE THE PRODUCT TABLE
    def create_post_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS post ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "date_created TEXT DEFAULT 'NULL' NOT NULL,"
                               "post TEXT DEFAULT 'NULL' NOT NULL,"
                               "image_url TEXT DEFAULT 'NULL' NOT NULL,"
                               "likes_amount TEXT DEFAULT 'NULL' NOT NULL,"
                               "user_id INTEGER NOT NULL,"
                               "FOREIGN KEY (user_id) REFERENCES user (id))")

        return "post table created successfully"

    #   FUNCTION WILL CREATE THE PRODUCT TABLE
    def create_comment_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS comment ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "date_created TEXT DEFAULT 'NULL' NOT NULL,"
                               "comment TEXT DEFAULT 'NULL' NOT NULL,"
                               "user_id INTEGER NOT NULL,"
                               "post_id INTEGER NOT NULL,"
                               "FOREIGN KEY (user_id) REFERENCES user (id), "
                               "FOREIGN KEY (post_id) REFERENCES post (id))")

        return "comment table created successfully"

    #   FUNCTION WILL CREATE THE PRODUCT TABLE
    def create_friendship_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS friendship ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "date_started TEXT DEFAULT 'NULL' NOT NULL,"
                               "user_id INTEGER NOT NULL,"
                               "friend_id INTEGER NOT NULL,"
                               "FOREIGN KEY (user_id) REFERENCES user (id), "
                               "FOREIGN KEY (friend_id) REFERENCES user (id))")

        return "friendship table created successfully"

    #   FUNCTION WILL CREATE THE PRODUCT TABLE
    def create_like_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS like ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                               "like TEXT DEFAULT 'inactive' NOT NULL,"
                               "user_id INTEGER NOT NULL, "
                               "post_id INTEGER NOT NULL, "
                               "FOREIGN KEY (user_id) REFERENCES user (id), "
                               "FOREIGN KEY (post_id) REFERENCES post (id))")

        return "like table created successfully"

    # USER FUNCTIONS ===================================================================================================
    #   FUNCTION WILL GET ALL THE USERS IN THE DATABASE AND RETURN THEM
    def get_users(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user")

            return cursor.fetchall()

    #   FUNCTION WILL GET A SPECIFIC USER BASED ON THE user_id
    def get_user_by_id(self, user_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM user WHERE id={str(user_id)}")

            return cursor.fetchone()

    #   FUNCTION WILL REGISTER A NEW USER
    def register_user(self, password, username, email_address):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO user( password, username, email_address ) "
                           f"VALUES( '{password}', '{username}', '{email_address}' )")

            connection.commit()
        return "user successfully registered"

    #   FUNCTION WILL LOG A REGISTERED USER IN
    def get_user(self, username, password):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}'")

            return cursor.fetchone()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_user(self, user_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM user WHERE id='{user_id}'")

            connection.commit()
        return "user deleted"

    def update_user(self, id, bio, password, username, fullname, phone_number, email_address):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE user SET bio = '{bio}', password = '{password}', username = '{username}', "
                           f"fullname = '{fullname}', phone_number = '{phone_number}', email_address = '{email_address}' "
                           f"WHERE id = '{id}'")

            connection.commit()
        return "user edited"

    # POST FUNCTIONS ===================================================================================================
    #   FUNCTION WILL SAVE A PRODUCT TO THE DATABASE
    def create_post(self, user_id, post, image_url, date_created):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO post( user_id, post, image_url, date_created) "
                           f"VALUES( '{user_id}', '{post}', '{image_url}', '{date_created}' )")

            connection.commit()

            return "post successfully created"

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_posts(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM post")

            return cursor.fetchall()

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_user_posts(self, user_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM post WHERE user_id = '{user_id}'")

            return cursor.fetchall()

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def update_post(self, post_id, post, image_url):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"UPDATE post "
                           f"SET post = '{post}', image_url = '{image_url}' "
                           f"WHERE id = '{post_id}'")

            return cursor.fetchall()

    #   FUNCTION WILL GET A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def get_post(self, post_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM post WHERE id={str(post_id)}")

            return cursor.fetchone()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_post(self, post_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM post WHERE id='{post_id}'")

            connection.commit()
        return "post deleted"

    # COMMENT FUNCTIONS ================================================================================================
    #   FUNCTION WILL SAVE A PRODUCT TO THE DATABASE
    def create_comment(self, user_id, comment, post_id, date_created):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO comment( user_id, comment, post_id, date_created ) "
                           f"VALUES( '{user_id}', '{comment}', '{post_id}', '{date_created}' )")

            connection.commit()

            return "comment successfully added"

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_comments(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM comment")

            return cursor.fetchall()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_comment(self, comment_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM comment WHERE id='{comment_id}'")

            connection.commit()
        return "comment deleted"

    # FRIENDSHIP FUNCTIONS =============================================================================================
    def create_friendship(self, user_id, friend_id, date_started):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO friendship( user_id, friend_id, date_started ) "
                           f"VALUES( '{user_id}', '{friend_id}', '{date_started}' )")

            connection.commit()
            return "friendship started"

    def get_friends(self, user_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM friendship WHERE user_id='{user_id}'")

        return cursor.fetchall()

    def end_friendship(self, user_id, friend_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM friendship WHERE user_id='{user_id}' AND friend_id='{friend_id}'")

            connection.commit()
        return "friendship ended"

    # LIKE FUNCTIONS ===================================================================================================
    def add_like(self, user_id, post_id):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO like( like, user_id, post_id ) "
                           f"VALUES( 'active', '{user_id}', '{post_id}' )")

            connection.commit()
        return "like added"

    def get_likes(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.row_factory = self.utilities.dict_factory
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM like")

        return cursor.fetchall()