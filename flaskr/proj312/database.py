import os
import sqlite3
import pymysql
from flask import g


class Database:
    def __init__(self):
        self.con = pymysql.connect(host='localhost',
                                   user='root',
                                   password='sesame24',
                                   db='db',
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)
        self.cur = self.con.cursor()

        self.post_table = "CREATE TABLE IF NOT EXISTS post(" \
                          "id INT(11) NOT NULL AUTO_INCREMENT," \
                          "created TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " \
                          "title VARCHAR(255) NOT NULL," \
                          "image VARCHAR(24) NOT NULL," \
                          "username VARCHAR(80) NOT NULL," \
                          "primary key (id))"

        self.comment_table = "CREATE TABLE IF NOT EXISTS comment(" \
                             "id INT(11) NOT NULL, " \
                             "created TIMESTAMP DEFAULT CURRENT_TIMESTAMP," \
                             "username VARCHAR(80), " \
                             "comment VARCHAR(5000) NOT NULL)"

        self.user_table = "CREATE TABLE IF NOT EXISTS user (" \
                          "id INT(11) NOT NULL AUTO_INCREMENT," \
                          "username VARCHAR(24) NOT NULL," \
                          "password VARCHAR(124) NOT NULL," \
                          "primary key (id))"

        self.vote_table = "CREATE TABLE IF NOT EXISTS votes(" \
                          "id INT(11) NOT NULL AUTO_INCREMENT, " \
                          "user_id INT(11) NOT NULL," \
                          "post_id INT(11) NOT NULL," \
                          "value INT(11) NOT NULL," \
                          "primary key (id))"

        self.cur.execute(self.post_table)
        self.cur.execute(self.comment_table)
        self.cur.execute(self.user_table)
        self.cur.execute(self.vote_table)

    def get_user_account_by_id(self, id):
        query = "SELECT * FROM user WHERE id = (%s)"
        self.cur.execute(query, (id,))
        ret = self.cur.fetchone()
        return ret

    def check_if_username_available(self, username: str):
        query = "SELECT * FROM user where username = (%s)"
        self.cur.execute(query, (username,))
        ret = self.cur.fetchall()
        return ret

    def get_user_account(self, username: str):
        query = "SELECT * FROM user where username = (%s)"
        self.cur.execute(query, (username,))
        ret = self.cur.fetchone()
        return ret

    def add_user(self, username: str, hashed_password: str):
        query = "INSERT INTO user (username, password) VALUES (%s, %s)"
        self.cur.execute(query, (username, hashed_password))
        self.con.commit()

    def insert_post(self, title: str, image: str):
        query = "INSERT INTO post (title, image, username) VALUES (%s, %s, %s)"
        self.cur.execute(query, (title, image, g.user['username']))
        self.con.commit()

    def query_top_10_posts(self):
        query = "SELECT * FROM post ORDER BY created desc LIMIT 10"
        self.cur.execute(query)
        top_10 = self.cur.fetchall()
        return top_10

    def query_top_post(self):
        query = "SELECT * FROM post ORDER BY created desc LIMIT 1"
        self.cur.execute(query)
        top_post = self.cur.fetchone()
        return top_post

    def query_post_by_id(self, id):
        query = "SELECT * FROM post WHERE id = (%s)"
        self.cur.execute(query, (id,))
        top_post = self.cur.fetchone()
        return top_post

    def change_vote_value(self, postid: int, vote_value: int):
        query = "UPDATE post SET votes = votes + (%s) WHERE id = (%s)"
        self.cur.execute(query, (vote_value, postid))
        self.con.commit()

    def insert_comment(self, postid, comment, username):
        query = "INSERT INTO comment (id, comment, username) VALUES (%s, %s, %s)"
        self.cur.execute(query, (postid, comment, username))
        self.con.commit()

    def get_posts_comments(self, postid):
        query = "SELECT * FROM comment WHERE id = (%s)"
        self.cur.execute(query, (postid,))
        comments = self.cur.fetchall()
        return comments

    def get_posts_votes(self, post_id):
        query = "SELECT * FROM votes WHERE post_id = (%s)"
        self.cur.execute(query, (post_id,))
        votes = self.cur.fetchall()
        return votes

    def get_users_vote(self, post_id, user_id):
        query = "SELECT * FROM votes WHERE post_id = (%s) AND user_id = (%s)"
        print(query)
        self.cur.execute(query, (post_id, user_id))
        vote = self.cur.fetchone()
        return vote
        #returns none if havent voted or a dict if they have

    def set_users_vote(self, post_id, user_id, val):
        query = "UPDATE votes SET value = (%s) WHERE post_id = (%s) AND user_id = (%s)"
        self.cur.execute(query, (val, post_id, user_id))
        self.con.commit()

    def add_vote(self, post_id, user_id, val):
        query = "INSERT INTO votes (post_id, user_id, value) VALUES (%s, %s, %s)"
        self.cur.execute(query, (post_id, user_id, val))
        self.con.commit()
