from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from Diary.auth import login_required
from Diary.db import get_db

import os
import datetime

import sys

BASE_DIR = os.path.dirname(__file__)



bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username, file_upload"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id,  title, body, created, author_id, username, file_upload"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, flash("Post id {id} doesn't exist."))

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        tmpfilename = ""
        uploadFlag = False
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y%m%d%H%M%S')

        if request.files['file']:
            tmpfilename = request.files['file'].filename
            tmpfilename = str(g.user["id"])+ '_' + str(nowDatetime) + '_' + tmpfilename
            uploadFlag = True
        

        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id, file_upload, file_upload_time) VALUES (?, ?, ?, ?, ?)",
                (title, body, g.user["id"], tmpfilename, str(nowDatetime)),
            )
            db.commit()

            if uploadFlag:
                f = request.files["file"]
                fname = (f.filename) 
                path =  os.path.join(BASE_DIR+"\\static\\upload\\", str(g.user["id"])+ '_' + str(nowDatetime) + '_' + fname)
                f.save(path)

            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]

        tmpfilename = ""
        uploadFlag = False
        now = datetime.datetime.now()
        nowDatetime = now.strftime('%Y%m%d%H%M%S')



        if request.files['file_name']:

            f = request.files['file_name']
            tmpfilename = f.filename 
            tmpfilename = str(g.user["id"])+ '_' + str(nowDatetime) + '_' + tmpfilename
            uploadFlag = True

        error = None
        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:

            if uploadFlag:
                db = get_db()
                db.execute(
                    "UPDATE post SET title = ?, body = ?, file_upload = ? WHERE id = ?", (title, body, tmpfilename, id)
                )
                db.commit()

                f = request.files["file_name"]
                fname = (f.filename) 
                path =  os.path.join(BASE_DIR+"\\static\\upload\\", str(g.user["id"])+ '_' + str(nowDatetime) + '_' + fname)
                f.save(path)

            else:
                db = get_db()
                db.execute(
                    "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
                )
                db.commit()


            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
