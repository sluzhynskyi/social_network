from flask import request, abort, g, jsonify
from flask import current_app as app
import uuid  # public id generation
from ..models import db, auth, Like, like_schema, likes_schema


@app.route('/posts/<int:post>/likes', methods=['Post'])
@auth.login_required
def post_like_unlike(post):
    """
    Like post or unlike (like toggle)
    :param post: int
    :return: json
    """
    like = Like.query.filter_by(user_id=g.user.username, post_id=post).first()
    if not like:
        like = Like(user_id=g.user.username, post_id=post, public_id=int(uuid.uuid4().time))
        db.session.add(like)
        like.state = False
    like.state = not like.state
    db.session.commit()
    return like_schema.jsonify(like)


@app.route('/posts/<int:post>/likes', methods=['Get'])
@auth.login_required
def get_all_likes(post):
    """
    Returns all likes that has this post
    :param post: int
    :return: json
    """
    likes = Like.query.filter_by(post_id=post).all()
    if likes:
        return likes_schema.jsonify(likes)
    return abort(404)
