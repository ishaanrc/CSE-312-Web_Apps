import os

from flask import (Blueprint, flash, render_template, request)
from flask_socketio import emit
from . import socketio
from . import db
from flask import g
bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'proj312/static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


@bp.route('/')
def home():
    the_posts = db.query_top_10_posts()
    new_list_of_dics = []
    for row in the_posts:
        print(str(row['id']))
        new_list_of_dics.append((row, db.get_posts_comments(row['id'])))

    greeting_text = "Hello, Please Login"
    bool_logged_in = False
    if g.user is not None:
        greeting_text = "Welcome, "+g.user['username']
        bool_logged_in = True
    return\
        render_template('home.html', posts=new_list_of_dics, greeting_text=greeting_text, bool_logged_in=bool_logged_in)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@socketio.on('post update')
def distribute_post(message):
    this_post = db.query_top_post()

    emit('update received', {'id': str(this_post['id']),
                             'title': this_post['title'],
                             'image': this_post['image'],
                             "votes": str(this_post['votes'])}, broadcast=True)


@socketio.on('vote')
def distribute_vote(message):
    print(type(message['val']), message['val'])
    db.change_vote_value(message['id'], message['val'])

    new_vote_count = db.query_post_by_id(message['id'])
    emit('vote received', {'id': message['id'],
                           "vote": new_vote_count['votes']}, broadcast=True)


@socketio.on('comment')
def distribute_comment(message):
    db.insert_comment(message['id'], message['comment'])
    print(message['id'], message['comment'])
    emit('comment received', {'id': message['id'],
                              "comment": message['comment']}, broadcast=True)


@bp.route('/upload', methods=('GET', 'POST'))
def post():
    if request.method == 'POST':
        title = request.form['title']
        image = request.files['image']
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
            print(title, image_name)
            db.insert_post(title, image_name)

            return "Ok"
        flash(error)
    return "Not Ok"
