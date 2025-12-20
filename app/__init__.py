from flask import Flask


# Factory for creating new app
def create_app():
    app = Flask(__name__)

    # TODO: Make this an actual secret key.
    app.secret_key = 'secret'

    from app.core import core_bp
    from app.admin import admin_bp
    from app.doctor import doctor_bp
    from app.clerk import clerk_bp

    app.register_blueprint(core_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(clerk_bp)

    return app
