import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "supersecretkey"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'crypto_users.db')}"  # ✅ Ensure correct path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
