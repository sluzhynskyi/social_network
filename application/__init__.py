from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_httpauth import HTTPBasicAuth

db = SQLAlchemy()
ma = Marshmallow()
auth = HTTPBasicAuth()


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)
    # Configs
    app.config['SECRET_KEY'] = 'REALLY SECRET KEY'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # For not complaining in the console

    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        db.create_all()  # Create sql tables for our data models
    return app
