from flask import Flask
from flask_cors import CORS
from config import Config
from app.models.db import db
import os


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    with app.app_context():
        db.create_all()

    from app.routes.upload      import upload_bp
    from app.routes.dashboard   import dashboard_bp
    from app.routes.chatbot     import chatbot_bp
    from app.routes.export      import export_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(export_bp)

    return app