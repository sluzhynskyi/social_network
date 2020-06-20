from flask import request, abort, g, jsonify
from flask import current_app as app
import uuid  # public id generation
from ..models import db, auth, User, user_schema, users_schema, activity_schema
from datetime import datetime as dt


@auth.verify_password
def verify_password(usr_or_tkn, pwd):
    """
    Returns true if token or username + pwd were correct
    :param usr_or_tkn: str
    :param pwd: str
    :return: boolean
    """
    user = User.verify_auth_token(usr_or_tkn)
    if not user:
        user = User.query.filter(User.username == usr_or_tkn).first()
        if not user or not user.verify_password(pwd):
            return False
    g.user = user
    g.user.last_request = dt.utcnow()
    return True


@app.route('/users', methods=['GET'])
def get_all_users():
    """
    Returns json where noticed details about all users (users_schema)
    :return: json
    """
    return users_schema.jsonify(User.query.all())


@app.route('/users', methods=['POST'])
def new_user():
    """
    Register new user, from username and password that comes from body json
    Returns json where noticed details about this user that was registered(user_schema)
    :param username: str
    :param password:  str
    :return: json
    """
    username = request.json['username']
    password = request.json['password']
    if username and password:
        if User.query.filter_by(username=username).first():
            return abort(409)  # Exists user with that username -> conflict
        user = User(username=username, public_id=int(uuid.uuid4().time))
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user)
    return abort(404)  # Not valid


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    """
    Returns json where noticed details about this user that (user_schema)
    :param username: str
    :return:  json
    """
    user = User.query.filter_by(username=username).first()
    if user:
        return user_schema.jsonify(user)
    return abort(404)


@app.route('/session', methods=['Post'])
@auth.login_required
def login():
    """
    Returns json in which is token based on expired-time (default 30min)
    :return: json
    """
    g.user.last_login = dt.utcnow()
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/session', methods=['Delete'])
@auth.login_required
def logout():
    """
    Makes logout from current account,
    :return: response
    """
    g.user = None
    return 'Logout', 200


@app.route('/users/<username>/activity', methods=['Get'])
@auth.login_required
def get_activity(username):
    """
    Returns user last login date, and last request date.
    :param username: str
    :return: json
    """
    user_activity = User.query.filter_by(username=username).first()
    if user_activity:
        return activity_schema.jsonify(user_activity)
    return abort(404)
