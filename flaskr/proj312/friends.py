from flask import (Blueprint, flash, g, session, redirect, render_template, request, url_for)

bp = Blueprint('friends', __name__)


@bp.route('/friends')
def friends():
    return render_template('friends.html')
