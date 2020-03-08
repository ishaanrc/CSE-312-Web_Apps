from flask import (Blueprint, flash, g, session, redirect, render_template, request, url_for)

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')
