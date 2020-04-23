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
