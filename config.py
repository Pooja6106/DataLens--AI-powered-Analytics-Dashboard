import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "datalens-secret-2024")

    # ── Build Database URL ──
    MYSQL_USER     = os.getenv("MYSQL_USER",     "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST     = os.getenv("MYSQL_HOST",     "localhost")
    MYSQL_PORT     = int(os.getenv("MYSQL_PORT", "3306") or "3306")
    MYSQL_DB       = os.getenv("MYSQL_DB",       "datalens")

    # Support full DATABASE_URL from Render/Railway/Heroku
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Render gives postgres:// — fix for SQLAlchemy
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER                  = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH             = int(
        os.getenv("MAX_CONTENT_LENGTH", "16777216") or "16777216")
    ANTHROPIC_API_KEY              = os.getenv("ANTHROPIC_API_KEY")
    GROQ_API_KEY                   = os.getenv("GROQ_API_KEY")