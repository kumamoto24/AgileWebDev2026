from app.models import User
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
