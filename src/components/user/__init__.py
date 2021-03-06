from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
import uuid
from src import login_manager,db,app
user_blueprint = Blueprint('userbp', __name__)
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
from src.models.users import User,Token,TokenRecover,Follow
from itsdangerous import URLSafeTimedSerializer
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
from src import app

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
  cloud_name = "hslqp9lo2", 
  api_key = "431569318637479", 
  api_secret = "5aLYTDDNtmlBX8MzWSpZGN4wxgs" 
)


##send email function
def send_simple_message(token, email, name):
	return requests.post(
		"https://api.mailgun.net/v3/mg.anhkhoa.dev/messages",
		auth=("api", app.config["API_MAIL_KEY"]),
		data={"from": "Mailgun Sandbox <postmaster@mg.anhkhoa.dev>",
			"to": f"<{email}>",
			"subject": f"Hello {name}",
		  "html": render_template("mails/recover.html", token = token)})

## 'host/user/'
@user_blueprint.route('/')
def root():
  return render_template('base/index.html')

@user_blueprint.route('/signup', methods=["GET", "POST"])
def signup():
  if current_user.is_authenticated:
    print("not need to login")
  if request.method == "POST":
    check_user = User.query.filter_by(email = request.json['email']).first()
    if not check_user:
      new_user = User(
          email = request.json['email'],
          address = request.json['address'],
          username = request.json['username']
      )
      new_user.set_password(request.json['password'])
      db.session.add(new_user)
      db.session.commit()
      return jsonify({
        "state" : "success"
      })
    else:
      return jsonify({
        "state": "duplicate"
      })
  return jsonify({
    "state":"nah"
  })

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@user_blueprint.route('/login', methods=["GET", "POST"])
def login():
    print(request.json['email'])
    user_query = User.query.filter_by(email = request.json['email']).first()
    if request.method == "POST":
      if user_query and user_query.check_password(request.json['password']):
        token_query = Token.query.filter_by(user_id=user_query.id)
        try:
            token = token_query.one()
        except NoResultFound:
            token = Token(user_id=user_query.id, uuid=str(uuid.uuid4().hex))
            db.session.add(token)
            db.session.commit()
        return jsonify({
            "state": True,
            "token": token.uuid
        })
      else:
        return jsonify({
          "state": False,
          "message" : "Password or email incorrect"
        })

@user_blueprint.route("/logout")
@login_required
def logout():
    token = Token.query.filter_by(user_id = current_user.id).first()
    if token:
      db.session.delete(token)
      db.session.commit()
      logout_user()
      return jsonify({
        "message":"success"
      })
    else:
      return jsonify({
        "message":"Failed"
      })

@user_blueprint.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
  if request.method == "POST":
    check_user = User.query.filter_by(email = request.json['email']).first()
    print("check_user", check_user)
    if not check_user:
      return jsonify({
        "message":"Email not exists"
      })
    else:
      token = ts.dumps(request.json['email'], salt='recover-password-secret')
      custom_token = f"{app.config['HOMEPAGE_URL']}/landing/new_password/{token}"
      response = send_simple_message(custom_token, request.json["email"], check_user.username)
      sent_token = TokenRecover.query.filter_by(email = request.json['email']).first()
      if sent_token:
        sent_token.token = token
        db.session.commit()
      else:
        sent_token = TokenRecover()
        sent_token.email = request.json['email']
        sent_token.token = token
        db.session.add(sent_token)
        db.session.commit()
      print("res", custom_token)
  return jsonify({
    "message":"Success"
  })

@user_blueprint.route("/new_password/<token>", methods=["POST", "GET"])
def new_password(token):
  if current_user.is_authenticated:
    return jsonify({
      "message":"Please logout current user first"
    })
  else:
    email_token = ts.loads(token, salt="recover-password-secret")
    token_valid = TokenRecover.query.filter_by(token = token).first()
    if token_valid:
      print(token_valid)
      if request.method == "POST":
        user = User.query.filter_by(email = email_token).first()
        user.set_password(request.json['password'])
        db.session.delete(token_valid)
        db.session.commit()
        return jsonify({
          "message":"Success"
        })
      else:
        return jsonify({
          "message":"valid"
        })
    else:
      return jsonify({
        "message":"invalid"
      })
    
  
  

@user_blueprint.route("/get_user", methods=["GET"])
@login_required
def get_user():
    return jsonify({
      "username": current_user.username,
      "email": current_user.email,
      "id": current_user.get_id(),
      "ava_url": current_user.ava_url
    })

@user_blueprint.route("/get_user/<id>", methods=["GET"])
@login_required
def get_user_by_id(id):
  user_query = User.query.get(id)
  return jsonify({
    "message":"success",
    "username":user_query.username,
    "user_id": user_query.id,
    "user_email": user_query.email,
    "created_at": user_query.convert_to_local(),
    "posts": user_query.get_posts(),
    "followings": user_query.get_followings(),
    "followers": user_query.get_followers(),
    "ava_url": user_query.ava_url
  })

@user_blueprint.route("/follow/<id>", methods=["POST"])
@login_required
def follow_user(id):
  user_query = User.query.get(id)
  if user_query:
    follow_query = Follow()
    follow_query.follower_id = current_user.id
    follow_query.main_id = id
    db.session.add(follow_query)
    db.session.commit()
  return jsonify({
    "message":"success",
    "followers": user_query.get_followers()
  })

@user_blueprint.route("/unfollow/<id>", methods=["DELETE"])
@login_required
def unfollow_user(id):
  user_query = User.query.get(id)
  currnet_user_following_list = current_user.get_followings()
  print(id , currnet_user_following_list)
  if user_query:
    print('run unfollow')
    unfollow_query = Follow.query.filter_by(main_id = id).filter_by(follower_id = current_user.id).first()
    db.session.delete(unfollow_query)
    db.session.commit()
  return jsonify({
    "message":"success",
    "followers": user_query.get_followers()
  })

@user_blueprint.route("/<id>/upload_ava", methods=["POST"])
@login_required
def upload(id):
  upload_ = cloudinary.uploader.upload(request.get_json()['file'])
  if id == current_user.id:
    current_user.ava_url = upload_['public_id']
  else:
    user_query = User.query.filter_by(id=id).first()
    user_query.ava_url = upload_['public_id']
  db.session.commit()
  return jsonify({
    "response":"success",
    "data":upload_['public_id']
  })