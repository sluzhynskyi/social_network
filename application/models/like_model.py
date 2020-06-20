from .. import db, ma
from datetime import datetime as dt


class Like(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))  # Private id
    user_id = db.Column(db.String(32), db.ForeignKey('users.username'))
    state = db.Column(db.BOOLEAN, nullable=False, default=True)  # Like and Unlike option
    date = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    public_id = db.Column(db.Integer, unique=True, nullable=False)  # Used to show this in output or in terminal

    def __repr__(self):
        return f'<Like {self.public_id}, {self.state}>'


# Post Schema
class LikeSchema(ma.Schema):
    class Meta:
        fields = ('post_id', 'user_id', 'date', 'state')


like_schema = LikeSchema()
likes_schema = LikeSchema(many=True)


# Analytics Schema
class AnalyticsSchema(ma.Schema):
    class Meta:
        fields = ('date', 'count')


analytics_schema = AnalyticsSchema(many=True)
