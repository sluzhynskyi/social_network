from flask import request, abort, g, jsonify
from flask import current_app as app
import uuid  # public id generation
from ..models import db, auth, User, user_schema, users_schema


@auth.verify_password
def verify_password(usr_or_tkn, pwd):
    user = User.verify_auth_token(usr_or_tkn)
    print(user, "Hello")
    if not user:
        user = User.query.filter(User.username == usr_or_tkn).first()
        if not user or not user.verify_password(pwd):
            return False
    g.user = user
    return True


@app.route('/users', methods=['GET'])
def get_all_users():
    return users_schema.jsonify(User.query.all())


@app.route('/users', methods=['POST'])
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


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user_schema.jsonify(user)
    return abort(404)


@app.route('/session', methods=['Post'])
@auth.login_required
def login():
    print("Im in")
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/session', methods=['Delete'])
@auth.login_required
def logout():
    g.user = None
    return 'Logout', 401
