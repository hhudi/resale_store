from app import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4


def validate_user(account, password):
    user = User.query.filter_by(account=account).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None
    return user

def register_user(account, password):
    if not account or not password:
        return None

    user = User.query.filter_by(account=account).first()
    if user:
        return None

    password_hash = generate_password_hash(password)
    user = User(sn=str(uuid4()).replace('-', ''),account=account, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    return user