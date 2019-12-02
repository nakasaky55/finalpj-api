from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from src import login_manager,db,app
user_blueprint = Blueprint('userbp', __name__)

from src.models.users import User
from itsdangerous import URLSafeTimedSerializer
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

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
    print("user exists ? ", user_query)
    
#   if request.method == "POST":
#     token_query = Token.query.filter_by(user_id=current_user.id)
#     try:
#         token = token_query.one()
#     except NoResultFound:
#         token = Token(user_id=current_user.id, uuid=str(uuid.uuid4().hex))
#         db.session.add(token)
#         db.session.commit()
    return jsonify({
        "state": "Success"
    })

@user_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("root"))

@user_blueprint.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
  if request.method == "POST":
    check_user = User.query.filter_by(email = request.form['email']).first()
    if not check_user:
      flash("Email invalid", "warning")
    else:
      token = ts.dumps(request.form['email'], salt='recover-password-secret')
      custom_token = f"http://localhost:5000/user/new_password/{token}"
      response = send_simple_message(custom_token, request.form["email"], check_user.username)
      print("res", custom_token)
      flash("Please check your mailbox", "danger")
  return render_template("user/forgot.html")

@user_blueprint.route("/new_password/<token>", methods=["POST", "GET"])
def new_password(token):
  if current_user.is_authenticated:
    return "Please logout current user first"
  else:
    email_token = ts.loads(token, salt="recover-password-secret")
    user = User.query.filter_by(email = email_token).first()
    if request.method == "POST":
      if request.form['password'] == request.form['confirm']:
        user.set_password(request.form['password'])
        db.session.commit()
        flash("Set password successfully", "primary")
        return redirect(url_for("userbp.login"))
      else:
        flash("Password does not match", "warning")
        return redirect(url_for("userbp.new_password", token = token))
  return render_template("user/newpassword.html")
  
