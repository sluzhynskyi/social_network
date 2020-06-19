from flask import current_app as app
from flask import request, abort
from ..models import db, Like, ma, analytics_schema

from sqlalchemy import func


@app.route('/analytics/', methods=['POST'])
def get_analytics():
    """"
    Returns analytics about how many likes was made, aggregated by day.
    :param date_from: str
    :param date_to: str
    :return json
    """
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    q = db.session.query(func.strftime("%Y-%m-%d", Like.date).label("date"), func.count(Like.id).label('count')).filter(Like.state == True,
                                                                                           Like.date > date_from,
                                                                                           Like.date < date_to).group_by(
        func.strftime("%Y-%m-%d", Like.date)).all()
    print(q)
    return analytics_schema.jsonify(q)
