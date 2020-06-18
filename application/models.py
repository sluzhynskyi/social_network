from flask import current_app as app
from . import db, ma, auth

from passlib.context import CryptContext  # Encrypting password

from datetime import timedelta as td  # Time managing
from datetime import datetime as dt

import jwt  # jwt token


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(32), index=True, nullable=False)
    password_hash = db.Column(db.String(64), nullable=False)
    posts = db.relationship('Post', backref='publisher')
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
        except Exception:
            return
        return User.query.get(data['username'])

    def __repr__(self):
        return f"<User {self.username}>"


# User Schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'username')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(80), nullable=False)
    body = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False,
                         default=dt.utcnow)
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.title}>'


# Post Schema
class PostSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'title', 'body', 'pub_date')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)
