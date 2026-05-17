from app.routes.auth import auth_bp
from app.routes.discovery import discovery_bp
from app.routes.main import main_bp
from app.routes.matches import matches_bp
from app.routes.messages import messages_bp
from app.routes.profiles import profiles_bp


def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(discovery_bp)
    app.register_blueprint(profiles_bp)
    app.register_blueprint(matches_bp)
    app.register_blueprint(messages_bp)
