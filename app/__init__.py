import os

from flask import Flask

from app.db import MongoDBStrategy, get_db


# Factory for creating new app
def create_app():
    app = Flask(__name__)

    app.secret_key = os.urandom(24)

    @app.context_processor
    def inject_db_type():
        # This runs before every template render and checks the DB currently in use
        current_strategy = get_db()

        if isinstance(current_strategy, MongoDBStrategy):
            return dict(current_db="MongoDB")
        else:
            return dict(current_db="MariaDB")

    from app.admin import admin_bp
    from app.clerk import clerk_bp
    from app.core import core_bp
    from app.doctor import doctor_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(clerk_bp)

    return app
