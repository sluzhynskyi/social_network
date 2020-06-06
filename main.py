from flask import Flask, abort, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_marshmallow import Marshmallow

from datetime import datetime, timedelta  # Time managing
from passlib.context import CryptContext  # Encrypting password

import uuid  # public id generation
import jwt  # jwt token
import os

# Init app
app = Flask(__name__)

# Configs
app.config['SECRET_KEY'] = 'REALLY SECRET KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # For not complaining in the console

# extensions
db = SQLAlchemy(app)  # Init database
ma = Marshmallow(app)  # Init marshmallow
auth = HTTPBasicAuth()


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

    def generate_auth_token(self, expires_in=timedelta(minutes=30)):
        return jwt.encode(
            {'public_id': self.public_id, 'exp': datetime.utcnow() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except Exception:
            return
        return User.query.get(data['id'])

    def __repr__(self):
        return f"<User {self.username}>"


@auth.verify_password
def verify_password(usr_or_tkn, pwd):
    user = User.verify_auth_token(usr_or_tkn)
    if not user:
        user = User.query.filter(User.username == usr_or_tkn).first()
        if not user or not user.verify_password(pwd):
            return False
    g.user = user
    return True


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
                         default=datetime.utcnow)
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<Post {self.title}>'


# Post Schema
class PostSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'title', 'body', 'pub_date')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)


@app.route('/api/register', methods=['POST'])
def new_user():
    username = request.json['username']
    password = request.json['password']
    if username and password:
        if User.query.filter_by(username=username).first():
            return abort(409)  # Exists user with that username -> conflict
        user = User(username=username, public_id=str(uuid.uuid4()))
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)
    return abort(404)  # Not valid


@app.route('/api/login', methods=['Post'])
@auth.login_required
def login():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/users', methods=['GET'])
def get_all_users():
    return users_schema.jsonify(User.query.all())


@app.route('/api/users/<int:public_id>', methods=['GET'])
def get_user(public_id):
    user = User.query.filter_by(publick_id=public_id).first()
    if user:
        return user_schema.jsonify(user)
    return abort(404)


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/api/posts', methods=['POST'])
@auth.login_required
def new_post():
    title = request.json['title']
    body = request.json['body']
    if title and body:
        post = Post(title=title, body=body, publisher_id=g.user.username)
        db.session.add(post)
        db.session.commit()
        return post_schema.jsonify(post)
    return abort(404)  # Not valid


@app.route('/api/posts', methods=['GET'])
@auth.login_required
def get_all_posts():
    """
    Gets all posts of all users
    :return: json
    """
    return posts_schema.jsonify(Post.query.all())


@app.route('/api/posts/<str:public_id>', methods=['GET'])
@auth.login_required
def get_one_post(public_id):
    """
    Gets only one post from all users
    :param public_id: str
    :return: json
    """
    post = Post.query.filter_by(public_id=public_id).first()
    return post_schema.jsonify(post)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
