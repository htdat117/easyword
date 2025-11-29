import logging

from flask import Flask
from flask_cors import CORS

from .config import FRONTEND_DIR
from .routes.report import report_bp
from .routes.static import static_bp


def create_app():
    """Application factory to create and configure the Flask app."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    app = Flask(__name__, static_folder=None)
    app.config["FRONTEND_DIR"] = str(FRONTEND_DIR)

    CORS(app)
    app.register_blueprint(report_bp)
    app.register_blueprint(static_bp)

    return app

