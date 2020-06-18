from flask import request, abort, g, jsonify
from flask import current_app as app
from .models import db, User, user_schema, users_schema
from .models import auth, Post, post_schema, posts_schema
import uuid  # public id generation


@app.route('/api/users', methods=['GET'])
def get_all_users():
    return users_schema.jsonify(User.query.all())


@app.route('/api/users/<public_id>', methods=['GET'])
def get_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if user:
        return user_schema.jsonify(user)
    return abort(404)


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


@auth.verify_password
def verify_password(usr_or_tkn, pwd):
    user = User.verify_auth_token(usr_or_tkn)
    if not user:
        user = User.query.filter(User.username == usr_or_tkn).first()
        if not user or not user.verify_password(pwd):
            return False
    g.user = user
    return True


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


@app.route('/api/posts/<public_id>', methods=['GET'])
@auth.login_required
def get_one_post(public_id):
    """
    Gets only one post from all users
    :param public_id: str
    :return: json
    """
    post = Post.query.filter_by(public_id=public_id).first()
    return post_schema.jsonify(post)
