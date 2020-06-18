from flask import request, abort, g, jsonify
from flask import current_app as app
import uuid  # public id generation
from ..models import db, auth, Post, post_schema, posts_schema


@app.route('/posts', methods=['POST'])
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


@app.route('/posts', methods=['GET'])
@auth.login_required
def get_all_posts():
    """
    Gets all posts of all users
    :return: json
    """
    return posts_schema.jsonify(Post.query.all())


@app.route('/posts/<public_id>', methods=['GET'])
@auth.login_required
def get_one_post(public_id):
    """
    Gets only one post from all users
    :param public_id: str
    :return: json
    """
    post = Post.query.filter_by(public_id=public_id).first()
    return post_schema.jsonify(post)
