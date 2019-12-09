from src import db
import datetime
import pytz
from src.models.users import User

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('hastags.id'), primary_key=True),
    db.Column('page_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)

likes = db.Table('likes',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey(User.id), primary_key=True)
)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relation(User)
    hastags = db.relationship("Hastags", secondary=tags)
    likes = db.relationship("User", secondary=likes, backref='post')
    
    def convert_to_local(self):
        LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        return self.created_at
    
    def get_user_like(self):
        users =[]
        for like in self.likes:
            users.append(like.get_id())
        return users

class Hastags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)





db.create_all()