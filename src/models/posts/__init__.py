from src import db
import datetime
import pytz
# from src.models.users import User

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('hastags.id'), primary_key=True),
    db.Column('page_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
)

likes = db.Table('likes',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id',ondelete="cascade"), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey("users.id",ondelete="cascade"), primary_key=True)
)

comments = db.Table('comments',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id',ondelete="cascade"), primary_key=True),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id',ondelete="cascade"), primary_key=True)
)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User")
    hastags = db.relationship("Hastags", secondary=tags)
    likes = db.relationship("User", secondary=likes, backref='post')
    comments = db.relationship("Comment", secondary=comments)
    
    def convert_to_local(self):
        LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        return self.created_at.strftime("%m/%d/%Y, %H:%M:%S")
    
    def get_user_like(self):
        users =[]
        for like in self.likes:
            users.append(like.get_id())
        return users

    def get_comments(self):
        comments_ = []
        for commt in self.comments:
            comments_.append({
                "content": commt.content,
                "author": commt.get_author(),
                "created_at": commt.get_created_at()
            })
        return comments_

    def get_like_number(self):
        if len(self.likes) > 0:
            return len(self.likes)
        else:
            return 0
    
    def get_comments_number(self):
        if len(self.comments) > 0:
            return len(self.comments)
        else:
            return 0
    def check_like(self, id):
        if(id in self.get_user_like()):
            return True
        else:
            return False

class Hastags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("users")

    def get_author(self):
        return self.author.username

    def get_created_at(self):
        return self.created_at.strftime("%m/%d/%Y, %H:%M:%S")





db.create_all()