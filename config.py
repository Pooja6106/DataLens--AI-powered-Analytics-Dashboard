import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY                  = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI     = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER               = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH          = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))
    ANTHROPIC_API_KEY           = os.getenv("ANTHROPIC_API_KEY")
# ```

# ---

# ### `.env`
# ```
# FLASK_ENV=development
# FLASK_SECRET_KEY=datalens-secret-2024
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_mysql_password_here
# MYSQL_DB=datalens
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# UPLOAD_FOLDER=uploads
# MAX_CONTENT_LENGTH=16777216
# ```

# ---

# ### `.gitignore`
# ```
# venv/
# __pycache__/
# *.pyc
# .env
# uploads/
# *.db
# instance/