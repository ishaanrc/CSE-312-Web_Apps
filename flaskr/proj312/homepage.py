import os

from flask import (Blueprint, flash, g, session, redirect, render_template, request, url_for)
from werkzeug.utils import secure_filename

from proj312.database import get_db

bp = Blueprint('main', __name__)

UPLOAD_FOLDER = 'imageuploads'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg'])

@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/', methods=('GET', 'POST'))
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
        elif '<' in title or '>' in title or '&' in title:
            error = "Please don't use a banned character"
        elif not image:
            error = "Please select an image"

        if error is None:
            imagename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, imagename))
            db.execute(
                'INSERT INTO post (title, image) VALUES (?, ?)',
                (title, imagename)
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

            return render_template('home.html')
        flash(error)
    return render_template('home.html')