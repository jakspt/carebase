from flask import Flask

# Factory for creating new app
def create_app():
    app = Flask(__name__)

    # TODO: Import Blueprints
    # TODO: Register Blueprints
    from app.doctor import doctor_bp
    app.register_blueprint(doctor_bp)

    return app