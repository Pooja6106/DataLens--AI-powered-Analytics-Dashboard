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
    app.config["SECRET_KEY"] = os.getenv(
        "FLASK_SECRET_KEY", "datalens-secret-2024")

    CORS(app)
    db.init_app(app)

    upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️  DB init warning: {e}")

    from app.routes.upload    import upload_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.chatbot   import chatbot_bp
    from app.routes.export    import export_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(export_bp)

    return app