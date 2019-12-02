from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, login_required
from flask_moment import Moment
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config.Config')
moment = Moment(app)
moment.init_app(app)
CORS(app)
db = SQLAlchemy(app)

migrate = Migrate(app, db)

login_manager= LoginManager(app)

from src.components.user import user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')

@app.route("/")
def root():
    return "Hello world!"