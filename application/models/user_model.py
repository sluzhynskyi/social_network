from flask import current_app as app
from flask import abort
from .. import db, ma, auth

from passlib.context import CryptContext  # Encrypting password

from datetime import timedelta as td  # Time managing
from datetime import datetime as dt

import jwt  # jwt token


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # Private id
    public_id = db.Column(db.Integer, unique=True, nullable=False)  # This id is used to show this in output
    username = db.Column(db.String(32), index=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)  # Hashed password for better security
    posts = db.relationship('Post', backref='publisher')
    likes = db.relationship('Like', backref='publisher')
    ctx = CryptContext(["sha256_crypt"])
    # For User-activity features
    last_login = db.Column(db.DateTime, nullable=False,
                           default=dt.utcnow)
    last_request = db.Column(db.DateTime, nullable=False,
                             default=dt.utcnow)

    def hash_password(self, password):
        """
        Returns encrypted password from real-one
        :param password: str
        :return: str
        """
        self.password_hash = User.ctx.hash(password)

    def verify_password(self, password):
        """
        Returns true when password is correct
        :param password: str
        :return: boolean
        """
        return User.ctx.verify(password, self.password_hash)

    def generate_auth_token(self, expires_in=td(minutes=30)):
        """
        Returns jwt token for jwt-authentication
        :param expires_in: timedelta
        :return: str
        """
        return jwt.encode(
            {'username': self.username, 'exp': dt.utcnow() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        """
        Returns true when token is correct
        :param token: str
        :return: boolean
        """
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


# UserActivity Schema
class ActivitySchema(ma.Schema):
    class Meta:
        fields = ('last_login', 'last_request')


activity_schema = ActivitySchema()
