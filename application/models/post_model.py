from .. import db, ma
from datetime import datetime as dt


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)  # Private id
    public_id = db.Column(db.Integer, unique=True, nullable=False)  # This id is used to show this in output
    title = db.Column(db.String(80), nullable=False)  # Tittle of your post
    body = db.Column(db.Text, nullable=False)  # Body-text of your post
    pub_date = db.Column(db.DateTime, nullable=False,
                         default=dt.utcnow)
    publisher_id = db.Column(db.Integer, db.ForeignKey('users.username'))
    likes = db.relationship('Like', backref='post')

    def __repr__(self):
        return f'<Post {self.title}>'


# Post Schema
class PostSchema(ma.Schema):
    class Meta:
        fields = ('public_id', 'title', 'body', 'pub_date', 'publisher_id')


post_schema = PostSchema()
posts_schema = PostSchema(many=True)
