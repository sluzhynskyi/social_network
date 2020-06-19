from flask import current_app as app
from flask import abort
from .. import db, ma, auth

from passlib.context import CryptContext  # Encrypting password

from datetime import timedelta as td  # Time managing
from datetime import datetime as dt

import jwt  # jwt token


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    posts = db.relationship('Post', backref='publisher')
    likes = db.relationship('Like', backref='publisher')
    ctx = CryptContext(["sha256_crypt"])

    def hash_password(self, password):
        self.password_hash = User.ctx.hash(password)

    def verify_password(self, password):
        return User.ctx.verify(password, self.password_hash)

    def generate_auth_token(self, expires_in=td(minutes=30)):
        return jwt.encode(
            {'username': self.username, 'exp': dt.utcnow() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except Exception as e:
            return False
        return User.query.filter(User.username == data['username']).first()

    def __repr__(self):
        return f"<User {self.username}>"


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'username')


user_schema = UserSchema()
users_schema = UserSchema(many=True)
