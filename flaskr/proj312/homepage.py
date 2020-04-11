import os

from flask import (Blueprint, flash, g, session, redirect, render_template, request, url_for)
from flask_socketio import SocketIO, emit
from . import socketio
from proj312.database import get_db

bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'proj312/static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

@bp.route('/')
def home():
    db = get_db()

    the_posts = db.execute('SELECT * FROM post ORDER BY created desc LIMIT 9').fetchall()
    new_list_of_dics = []
    for row in the_posts:
        print(str(row['id']))
        new_list_of_dics.append((row, db.execute('SELECT * FROM comment WHERE id = (?)', (str((row['id'])), )).fetchall()))

    return render_template('home.html', posts=new_list_of_dics)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@socketio.on('post update')
def distribute_post(message):
    db = get_db()
    this_post = db.execute('SELECT * FROM post ORDER BY created desc LIMIT 1').fetchone()
    print(this_post)

    print("Made it here")
    emit('update received', {'id': str(this_post['id']),
                             'title': this_post['title'],
                             'image': this_post['image'],
                             "votes": str(this_post['votes'])}, broadcast=True)


@socketio.on('vote')
def distribute_vote(message):
    db = get_db()
    print(type(message['val']), message['val'])
    db.execute(
        'UPDATE post SET votes = votes + (?) WHERE id = (?)', (message['val'], message['id'])
    )
    db.commit()
    new_vote_count = db.execute('SELECT * FROM post WHERE id = (?)', (message['id'],)).fetchone()
    emit('vote received', {'id': message['id'],
                           "vote": new_vote_count['votes']}, broadcast=True)
    print("new_vote_count:", new_vote_count['votes'])


@socketio.on('comment')
def distribute_comment(message):
    db = get_db()
    db.execute(
        'INSERT INTO comment (id, comment) VALUES (?, ?)',
        (message['id'], message['comment'])
    )
    db.commit()
    emit('comment received', {'id': message['id'],
                           "comment": message['comment']}, broadcast=True)

@bp.route('/upload', methods=('GET', 'POST'))
def post():
    if request.method == 'POST':
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

            return "Ok"
        flash(error)
    return "Not Ok"


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
                'UPDATE post SET votes = votes + 1 WHERE id = (?)',(pid,)
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
                'UPDATE post SET votes = votes - 1 WHERE id = (?)', pid
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




