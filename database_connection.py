import sqlite3


class Database:
    def __init__(self, database_name):
        self.database_name = database_name

    #   FUNCTION WILL CREATE THE USER TABLE
    def create_user_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS user("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "first_name TEXT NOT NULL,"
                               "last_name TEXT NOT NULL,"
                               "username TEXT NOT NULL,"
                               "email_address TEXT NOT NULL,"
                               "address TEXT NOT NULL,"
                               "password TEXT NOT NULL)")

        return "user table created successfully"

    #   FUNCTION WILL CREATE THE PRODUCT TABLE
    def create_product_table(self):
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS product("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                               "name TEXT NOT NULL,"
                               "description TEXT NOT NULL,"
                               "price TEXT NOT NULL,"
                               "category TEXT NOT NULL,"
                               "review TEXT NOT NULL)")

        return "product table created successfully"

    #   FUNCTION WILL GET ALL THE USERS IN THE DATABASE AND RETURN THEM
    def get_users(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM user")

            return cursor.fetchall()

    #   FUNCTION WILL REGISTER A NEW USER
    def register_user(self, first_name, last_name, username, email_address, address, password):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO user( first_name, last_name, username, email_address, address, password )"
                           f"VALUES( '{first_name}', '{last_name}', '{username}', '{email_address}', '{address}', '{password}' )")

            connection.commit()

        return "user successfully registered"

    #   FUNCTION WILL LOG A REGISTERED USER IN
    def get_user(self, username, password):
        #   THE WHERE CLAUSE WAS GIVING ISSUES SO I HAD TO FIND ALTERNATE WAY TO GET THE USER
        #   GET ALL THE users FROM THE DATABASE
        users = self.get_users()
        #   LOOP THROUGH ALL THE users
        for user in users:
            #   CHECK IF THE user's USERNAME AND PASSWORD IS EQUAL TO THE username AND password PROVIDED
            if user[3] == username and user[5] == password:
                #   RETURN THE user
                return user

    #   FUNCTION WILL SAVE A PRODUCT TO THE DATABASE
    def save_product(self, name, description, price, category, review):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO product( name, description, price, category, review )"
                           f"VALUES( '{name}', '{description}', '{price}', '{category}', '{review}' )")

            connection.commit()

            return "product successfully added"

    #   FUNCTION WILL GET ALL THE PRODUCTS FROM THE DATABASE AND RETURN THEM
    def get_all_products(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM product")

            return cursor.fetchall()

    #   FUNCTION WILL GET A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def get_one_product(self, product_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM product WHERE id={str(product_id)}")

            return cursor.fetchone()

    #   FUNCTION WILL DELETE A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def remove_product(self, product_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"DELETE FROM product WHERE id={str(product_id)}")

            connection.commit()
        return "product deleted"

    #   FUNCTION WILL EDIT A PRODUCT FROM THE DATABASE WHICH MATCHES THE PROVIDED ID
    def update_product(self, row_name, new_value, product_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE product SET {row_name} = '{str(new_value)}' WHERE id = {str(product_id)}")

            connection.commit()
        return "product edited"

    def update_again(self, name, description, price, category, review, product_id):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            cursor.execute(f"UPDATE product SET name = {name}, description = '{description}', price = '{price}', "
                           f"category = '{category}', review = {review} WHERE id = {str(product_id)}")
            print("edited")
