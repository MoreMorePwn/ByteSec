from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    app.config.update(
        SECRET_KEY="dev-change-me-in-production",
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{instance_path / 'bytesec.db'}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    app.config.from_pyfile("config.py", silent=True)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    from . import models  # noqa: F401
    from .routes import bp

    app.register_blueprint(bp)

    @app.cli.command("init-db")
    def init_db_command():
        from .seed import seed_database

        seed_database()
        print("Database initialized with SQLi course data.")

    @app.cli.command("ensure-db")
    def ensure_db_command():
        from .seed import ensure_database

        ensure_database()

    @app.cli.command("refresh-course")
    def refresh_course_command():
        from .seed import refresh_course_content

        refresh_course_content()
        print("Course content refreshed from markdown without deleting users.")

    return app
