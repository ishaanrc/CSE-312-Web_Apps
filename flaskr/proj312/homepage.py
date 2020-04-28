import os

from flask import (Blueprint, flash, render_template, request)
from flask_socketio import emit

from proj312.log import login_required
from . import socketio
from . import db
from flask import g, session
bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'proj312/static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])


@bp.route('/')
def home():
    the_posts = db.query_top_10_posts()
    new_list_of_dics = []
    for row in the_posts:
        get_post_votes(row)
        new_list_of_dics.append((row, db.get_posts_comments(row['id'])))

    greeting_text = "Hello, Please Login"
    bool_logged_in = False
    friends = []
    messages = []
    if g.user is not None:
        greeting_text = "Welcome, "+g.user['username']
        bool_logged_in = True
        friends = db.get_user_accounts_except_one(g.user['id'])
        check_all_friends_status(friends)
        messages = db.get_users_recent_messages(g.user['id'])

    return render_template('home.html',
                           posts=new_list_of_dics,
                           greeting_text=greeting_text,
                           bool_logged_in=bool_logged_in,
                           friends=friends,
                           messages=messages)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@socketio.on('friend_request')
def add_friendship(message):
    if session['user_id'] is not None:
        friends = db.check_friendship(session['user_id'], message['id'])
        if friends is None:
            db.add_friendship(session['user_id'], message['id'])
        print(db.check_friendship(session['user_id'], message['id']))


@socketio.on('post update')
def distribute_post(message):
    this_post = db.query_top_post()
    cur_user = db.get_user_account_by_id(session['user_id'])
    emit('update received', {'id': str(this_post['id']),
                             'title': this_post['title'],
                             'image': this_post['image'],
                             'username': cur_user['username'],
                             "votes": str(0)}, broadcast=True)


@socketio.on('vote')
def distribute_vote(message):
    print(message)
    cur_user = db.get_user_account_by_id(session['user_id'])
    print(cur_user)

    current_vote = db.get_users_vote(message['id'], cur_user['id'])
    print(current_vote)

    if current_vote is None:
        db.add_vote(message['id'], cur_user['id'], message['val'])
        #Add their particular vote to vote table, tell everyone inc or dec by one
        emit('vote received', {'id': message['id'],
                               "vote": message['val']}, broadcast=True)
    elif current_vote['value'] == message['val']:
        #Corresponds to them trying to upvote/downvote a second time, not allowed so do nothing
        pass
    else:
        db.set_users_vote(message['id'], cur_user['id'], message['val'])

        emit('vote received', {'id': message['id'],
                               "vote": message['val']*2}, broadcast=True)
        #The *2 above corresponds to them "unvoting" and revoting the opposite value



@socketio.on('comment')
def distribute_comment(message):
    cur_user = db.get_user_account_by_id(session['user_id'])

    db.insert_comment(message['id'], message['comment'], cur_user['username'])
    print(message['id'], message['comment'])
    emit('comment received', {'id': message['id'],
                              "comment": message['comment'],
                              'username': cur_user['username']}, broadcast=True)


@socketio.on('message')
def process_message(message):
    cur_user = db.get_user_account_by_id(session['user_id'])
    if cur_user is not None:
        if db.check_friendship(session['user_id'], message['id']) and db.check_friendship(message['id'], session['user_id']):
            print(message)
            db.add_message(cur_user['username'], session['user_id'], message['id'], message['message'])


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
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


def get_post_votes(post: dict):
    post_id = post['id']
    votes = db.get_posts_votes(post_id)
    vote_count = 0
    for vote in votes:
        vote_count += vote['value']
    post['votes'] = vote_count


def check_all_friends_status(other_users):
    my_id = session['user_id']
    for user in other_users:
        their_id = user['id']
        me_friends_them = db.check_friendship(my_id, their_id)
        them_friends_me = db.check_friendship(their_id, my_id)

        if me_friends_them is not None and them_friends_me is not None:
            user['friends'] = True
        else:
            user['friends'] = False
