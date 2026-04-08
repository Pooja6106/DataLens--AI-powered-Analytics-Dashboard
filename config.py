import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY   = os.getenv(
        "FLASK_SECRET_KEY", "datalens-secret-2024")

    DATABASE_URL = os.getenv("DATABASE_URL", "")

    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace(
                "postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        _port = os.getenv("MYSQL_PORT", "3306")
        _port = int(_port) if _port and _port.isdigit() else 3306
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://"
            f"{os.getenv('MYSQL_USER','root')}:"
            f"{os.getenv('MYSQL_PASSWORD','')}@"
            f"{os.getenv('MYSQL_HOST','localhost')}:"
            f"{_port}/"
            f"{os.getenv('MYSQL_DB','datalens')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER      = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH","16777216") or "16777216")
    GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
    ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY")