from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf

app = Flask(__name__)
app.config.from_object(Config)

csrf = CSRFProtect(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

socketio = SocketIO(app, async_mode="threading")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"  # where to redirect if not logged in


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)


from app import models, sockets, user_loader
from app.routes import register_blueprints

register_blueprints(app)
