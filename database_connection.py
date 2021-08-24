import sqlite3


class Database:
    def __init__(self, database_name):
        self.database_name = database_name

    #   FUNCTION WILL CREATE THE USER TABLE
    def create_user_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS user("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "fullname TEXT DEFAULT 'NULL' NOT NULL,"
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
            connection.execute("CREATE TABLE IF NOT EXISTS post("
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
            connection.execute("CREATE TABLE IF NOT EXISTS comment("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "date_created TEXT DEFAULT 'NULL' NOT NULL,"
                               "comment TEXT DEFAULT 'NULL' NOT NULL,"
                               "user_id INTEGER NOT NULL,"
                               "post_id INTEGER NOT NULL,"
                               "FOREIGN KEY (user_id) REFERENCES user (id), "
                               "FOREIGN KEY (post_id) REFERENCES post (id))")

        return "comment table created successfully"

    #   FUNCTION WILL GET ALL THE USERS IN THE DATABASE AND RETURN THEM
    def get_users(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user")

            return cursor.fetchall()

    #   FUNCTION WILL REGISTER A NEW USER
    def register_user(self, password, username, email_address):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO user( password, username, email_address ) "
                           f"VALUES( '{password}', '{username}', '{email_address}' )")

            connection.commit()
        return "user successfully registered"

    #   FUNCTION WILL LOG A REGISTERED USER IN
    def get_user(self, username, password):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM user WHERE username='{username}' AND password='{password}'")

            return cursor.fetchone()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_user(self, user_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM user WHERE id='{user_id}'")

            connection.commit()
        return "user deleted"


    #   FUNCTION WILL SAVE A PRODUCT TO THE DATABASE
    def create_post(self, user_id, post, image_url, date_created):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO post( user_id, post, image_url, date_created) "
                           f"VALUES( '{user_id}', '{post}', '{image_url}', '{date_created}' )")

            connection.commit()

            return "post successfully created"

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_posts(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM post")

            return cursor.fetchall()

    #   FUNCTION WILL GET A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def get_post(self, post_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM post WHERE id={str(post_id)}")

            return cursor.fetchone()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_post(self, post_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM post WHERE id='{post_id}'")

            connection.commit()
        return "post deleted"


    #   FUNCTION WILL SAVE A PRODUCT TO THE DATABASE
    def create_comment(self, user_id, comment, post_id, date_created):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO comment( user_id, comment, post_id, date_created ) "
                           f"VALUES( '{user_id}', '{comment}', '{post_id}', '{date_created}' )")

            connection.commit()

            return "comment successfully added"

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_comments(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM comment")

            return cursor.fetchall()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def delete_comment(self, comment_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM comment WHERE id='{comment_id}'")

            connection.commit()
        return "comment deleted"

