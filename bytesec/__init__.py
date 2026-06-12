import os
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me-in-production"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    # ── Database: Turso (production) or local SQLite (development) ──
    turso_url = os.environ.get("TURSO_DATABASE_URL")
    turso_token = os.environ.get("TURSO_AUTH_TOKEN")

    if turso_url and turso_token:
        # Turso via libsql-experimental HTTP client
        import libsql_experimental as libsql

        def get_turso_connection():
            return libsql.connect(
                database="",
                url=turso_url,
                auth_token=turso_token,
            )

        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "creator": get_turso_connection,
            "pool_pre_ping": True,
            "connect_args": {"check_same_thread": False},
        }
        # URI says sqlite because libsql speaks the same SQL dialect
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    else:
        # Local SQLite (development)
        app.config.update(
            SQLALCHEMY_DATABASE_URI=f"sqlite:///{instance_path / 'bytesec.db'}",
        )

    app.config.from_pyfile("config.py", silent=True)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    from . import models  # noqa: F401
    from .routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        from .seed import ensure_database

        ensure_database()

    @app.cli.command("init-db")
    def init_db_command():
        from .seed import seed_database

        seed_database()
        print("Database initialized with ByteSec course data.")

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
