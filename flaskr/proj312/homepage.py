import os
import sqlite3
from typing import List, Any

from flask import (Blueprint, flash, g, session, redirect, render_template, request, url_for)
from werkzeug.utils import secure_filename

from proj312.database import get_db

bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'proj312/static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

@bp.route('/')
def home():
    db = get_db()

    temp = db.execute('SELECT * FROM post ORDER BY votes desc LIMIT 10').fetchall()

    for post in temp:
        x = post['id']
        sql_statement = 'SELECT * FROM comment WHERE id = (?);'
        listOfDicts = db.execute(sql_statement, (x,)).fetchall()
        g = listOfDicts

        # def dict_factory(cursor, row):
        #     d = {}
        #     for idx, col in enumerate(cursor.description):
        #         d[col[0]] = row[idx]
        #     return d
        #
        # con = sqlite3.connect(":memory:")
        # con.row_factory = dict_factory()
        # cur = con.cursor()
        #
        #
        # for rows in listOfDicts:
        #     print(rows)

        # hi: List[Any] = []
        #
        #
        #
        # for i in listOfDicts:
        #     hi.append(i['comment'])

        #post.update({'comments' : hi})




    return render_template('home.html', posts=temp)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=('GET', 'POST'))
def post():
    if request.method == 'POST':
        print(request.form)
        print(request.files)
        title = request.form['title']
        image = request.files['image']
        db = get_db()
        error = None

        if not title:
            error = "Please include a title"
        elif '<' in title or '>' in title or '&' in title or ';' in title:
            error = "Please don't use a banned character"
        elif not image:
            error = "Please select an image"
        elif not allowed_file(image.filename):
            error = "Not allowed file"
        if error is None:
            direc_size = len(os.listdir(UPLOAD_FOLDER))
            image_name = str(direc_size) + "." + image.filename.rsplit('.', 1)[1].lower()
            image.save(os.path.join(UPLOAD_FOLDER, image_name))
            db.execute(
                'INSERT INTO post (title, image) VALUES (?, ?)',
                (title, image_name)
            )
            db.commit()

            # Following code just prints out the current contents of the db
            temp = db.execute(
                'SELECT * FROM post'
            ).fetchall()
            print(temp)
            for thing in temp:
                print(thing["title"] + " " + thing["image"])
            # End code that prints out the contents of the db

            return redirect(url_for("main.home"))
        flash(error)
    return redirect(url_for("main.home"))


@bp.route('/upvote', methods=('GET', 'POST'))
def upvote():
    if request.method == 'POST':
        #print(request.upvote)
        upvote = request.form['upvote']
        pid = request.form['postid']
        error = None
        db = get_db()

        if upvote != '1' and upvote != 1:
            error = "upvote not cast"
        if error == None:
            db.execute(
                'UPDATE post SET votes = votes + 1 WHERE id = (?)',pid
            )
            #db.commit()

            db.execute(
                'SELECT * FROM post ORDER BY votes'
            )
            db.commit()
            return redirect(url_for("main.home"))
        flash(error)
    return redirect(url_for("main.home"))


@bp.route('/downvote', methods=('GET', 'POST'))
def downvote():
    if request.method == 'POST':
        #sprint(request.downvote)
        upvote = request.form['downvote']
        pid = request.form['postid']
        error = None
        db = get_db()

        if upvote != '-1' and  upvote != -1:
            error = "Downvote Not Cast"
        if error == None:
            db.execute(
                'UPDATE post SET votes = votes - 1 WHERE id = (?)',pid
            )
            #db.commit()
            db.execute(
                'SELECT * FROM post ORDER BY votes'
            )
            db.commit()

            return redirect(url_for("main.home"))
        flash(error)
    return redirect(url_for("main.home"))




@bp.route('/uploadcomment', methods = ('GET', 'POST'))
def comment():
    if request.method == 'POST':

        comment = request.form['comment']
        pid = request.form['postid']

        error = None
        db = get_db()

        if not comment:
            error = "Comment not going through"
        if comment == "":
            error = "Comment can't be blank"
        if error == None:
            db.execute(
                'INSERT INTO comment (id, comment) VALUES (?, ?)',
                (pid, comment)
            )
            db.commit()

            return redirect(url_for("main.home"))
        flash(error)
    return redirect(url_for("main.home"))




