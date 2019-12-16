from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, login_required
from flask_moment import Moment
from flask_cors import CORS
import cloudinary
import cloudinary.uploader



app = Flask(__name__)
app.config.from_object('config.Config')
moment = Moment(app)
moment.init_app(app)
CORS(app)
db = SQLAlchemy(app)



migrate = Migrate(app, db)

login_manager= LoginManager(app)
from src.models.users import User,Token

@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            return token.user
    return None

from src.components.user import user_blueprint
app.register_blueprint(user_blueprint, url_prefix='/user')

from src.components.posts import posts_blueprint
app.register_blueprint(posts_blueprint, url_prefix='/posts')

@app.route("/")
def root():

    return "Hello world!"