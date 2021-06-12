import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "Diarydb.sqlite"),
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from Diary import db

    db.init_app(app)

    from Diary import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    app.add_url_rule("/", endpoint="index")

    return app
