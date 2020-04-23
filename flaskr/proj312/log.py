import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from passlib.hash import sha256_crypt
from . import db

bp = Blueprint('log', __name__, url_prefix='/log')


@bp.route('/register', methods=['POST', 'GET'])
def register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['pcheck']

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not password_check:
            error = 'Password is required.'
        elif password_check != password:
            error = 'Passwords must match'
        elif len(db.check_if_username_available(username)) != 0:
            error = "User already registered"

        if error is None:
            hashed_password = sha256_crypt.encrypt(password)
            db.add_user(username, hashed_password)
            return redirect(url_for('main.home'))

        flash(error)

    return render_template('register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        error = None
        user = db.get_user_account(username)

        if user is None:
            error = 'Incorrect username.'
        elif not sha256_crypt.verify(password, user['password']):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('main.home'))

        flash(error)
    return render_template('login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_account_by_id(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('log.login'))

        return view(**kwargs)

    return wrapped_view
