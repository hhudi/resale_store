from app import db
from datetime import datetime
from flask_login import AnonymousUserMixin
from uuid import uuid1

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(36), unique=True, default=str(uuid1()).replace('-',''))
    account = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    profile_image = db.Column(db.String(64))
    created_time = db.Column(db.DateTime, default=datetime.now)
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.id


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sn = db.Column(db.String(36), unique=True, default=str(uuid1()).replace('-',''))
    # sn = db.Column(db.String(36), unique=True, default=str(uuid4()))
    user_sn = db.Column(db.String(36), nullable=False)
    status = db.Column(db.Integer, default=0) # 0未发布, 1已发布, 2锁定中, 3已卖出, 4已删除
    name = db.Column(db.String(80))
    category = db.Column(db.Integer, default=0) # 0数码， 1书籍， 2其他
    price = db.Column(db.Integer, default=0)
    main_image = db.Column(db.String(64))
    describe = db.Column(db.String(500))
    created_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)

class ItemImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_sn = db.Column(db.String(36), nullable=False)
    filename = db.Column(db.String(64))
    is_main = db.Column(db.Boolean(), default=False)
    deleted = db.Column(db.Boolean(), default=False)
    created_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ItemOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    item_sn = db.Column(db.String(36), nullable=False)
    status = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.utcnow)