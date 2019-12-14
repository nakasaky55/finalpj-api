from flask_login import UserMixin
from src import db
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
from flask_login import current_user


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(255), nullable = False, unique = True)
    username = db.Column(db.String(255), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable=False, unique = False)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
    posts_created = db.relationship("Posts")
    mainid = db.relationship("Follow", foreign_keys="Follow.main_id", backref="follower")
    followings = db.relationship("Follow", foreign_keys="Follow.follower_id", backref="following")
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.id

    def convert_to_local(self):
        return self.created_at.strftime("%m/%d/%Y, %H:%M:%S")

    def get_posts(self):
        posts_ = []
        for post in self.posts_created:
            json_post = ({
                "id":post.id,
                "content":post.content,
                "created_at":post.created_at,
                "likes": post.get_user_like(),
                "comments": post.get_comments(),
                "like_state": post.check_like(current_user.id)
            })
            posts_.append(json_post)
        return posts_

    def get_followings(self):
        if len(self.followings) > 0:
            list_mainid = []
            for following in self.followings:
                list_mainid.append(following.following.id)
            return list_mainid
        return []

    def get_followers(self):
        if len(self.mainid) > 0:
            list_followings = []
            for following in self.mainid:
                list_followings.append(following.following.id)
            return list_followings
        return []

class Follow(db.Model):
    __tablename__ = "follow"
    id= db.Column(db.Integer, primary_key=True)
    main_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship(User)

class TokenRecover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

db.create_all()