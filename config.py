import os

from dotenv import load_dotenv

load_dotenv()


class Config:

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    DB_HOST = os.getenv("TIDB_HOST")
    DB_PORT = int(os.getenv("TIDB_PORT", 4000))
    DB_USER = os.getenv("TIDB_USER")
    DB_PASSWORD = os.getenv("TIDB_PASSWORD")
    DB_NAME = os.getenv("TIDB_DATABASE")

    CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")