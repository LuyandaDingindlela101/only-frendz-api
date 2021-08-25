import unittest
from database_connection import Database


class TestStringMethods(unittest.TestCase):
    def test_create_user_table(self):
        database = Database("test.db")
        self.assertEqual(database.create_user_table(), "user table created successfully")

    def test_create_post_table(self):
        database = Database("test.db")
        self.assertEqual(database.create_post_table(), "post table created successfully")

    def test_create_comment_table(self):
        database = Database("test.db")
        self.assertEqual(database.create_comment_table(), "comment table created successfully")

    def test_create_friendship_table(self):
        database = Database("test.db")
        self.assertEqual(database.create_friendship_table(), "friendship table created successfully")

    def test_register_user(self):
        database = Database("test.db")
        self.assertEqual(database.register_user("password", "username", "email_address"), "user successfully registered")

    def test_create_post(self):
        database = Database("test.db")
        self.assertEqual(database.create_post("1", "This is a post", "image url", "18-03-2021"), "post successfully created")

    def test_create_comment(self):
        database = Database("test.db")
        self.assertEqual(database.create_comment("1", "This is a comment", "1", "18-03-2021"), "comment successfully added")

    def test_delete_comment(self):
        database = Database("test.db")
        self.assertEqual(database.delete_comment("1"), "comment deleted")

    def test_delete_post(self):
        database = Database("test.db")
        self.assertEqual(database.delete_post("1"), "post deleted")

    def test_create_friendship(self):
        database = Database("test.db")
        self.assertEqual(database.create_friendship("1", "1", "18-03-2021"), "friendship started")

    def test_end_friendship(self):
        database = Database("test.db")
        self.assertEqual(database.end_friendship("1", "1"), "friendship ended")