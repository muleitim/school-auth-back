import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load variables from .env
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-very-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 3600       # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 604800    # 7 days

    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = True                  # ✅ REQUIRED for HTTPS
    JWT_COOKIE_SAMESITE = "None"              # ✅ REQUIRED for cross-origin cookies
    JWT_COOKIE_CSRF_PROTECT = False

    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:3000")
