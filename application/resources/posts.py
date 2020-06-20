from flask import request, abort, g
from flask import current_app as app
import uuid  # public id generation
from ..models import db, auth, Post, post_schema, posts_schema


@app.route('/posts', methods=['POST'])
@auth.login_required
def new_post():
    """
    Creates new post, from title and body text
    Returns json where noticed details about this post (post_schema)
    :param title: str
    :param body str
    :return: json
    """
    title = request.json['title']
    body = request.json['body']
    if title and body:
        post = Post(title=title, body=body, publisher_id=g.user.username, public_id=int(uuid.uuid4().time))
        db.session.add(post)
        db.session.commit()
        return post_schema.jsonify(post)
    return abort(404)  # Not valid


@app.route('/posts', methods=['GET'])
def get_all_posts():
    """
    Gets all posts of all users
    Returns json where noticed details about all posts (posts_schema)
    :return: json
    """
    return posts_schema.jsonify(Post.query.all())


@app.route('/posts/<int:public_id>', methods=['GET'])
def get_one_post(public_id):
    """
    Gets specific post from all users
    Returns json where noticed details about this (by public_id) post (post_schema)
    :param public_id: int
    :return: json
    """
    post = Post.query.filter_by(public_id=public_id).first()
    if post:
        return post_schema.jsonify(post)
    return abort(404)
