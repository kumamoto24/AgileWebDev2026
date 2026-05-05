import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #Google Map API key
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

    #Database key
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(basedir, "app.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False