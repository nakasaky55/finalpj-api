from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager,login_required, current_user
from src import login_manager,db,app
import datetime
from src.models.posts import Posts,Hastags,likes,Comment,tags
from operator import itemgetter

posts_blueprint = Blueprint('postsbp', __name__)

@posts_blueprint.route('/create', methods=['POST','GET'])
@login_required
def create_post():
    # print(request.json['hastags'])
    new_post = Posts()
    new_post.user_id = current_user.id
    new_post.created_at = datetime.datetime.now()
    new_post.content = request.json['content']
    db.session.add(new_post)
    db.session.commit()
    if len(request.json['hastags']) > 0:
        for hastag in request.json['hastags']:
            # print("current hastag in loop", hastag)
            query_hastag = Hastags.query.filter_by(description = hastag).first()
            if not query_hastag:
                new_hastag = Hastags()
                new_hastag.description = hastag
                new_post.hastags.append(new_hastag)
            else:
                print("has tag is existed, ", hastag)
                new_post.hastags.append(query_hastag)
        db.session.commit()
    return jsonify({
        "message":"created"
    })


@posts_blueprint.route('/get_posts/post&page=<int:page>', methods=["GET"])
# @login_required
def get_posts(page):
    following_list = current_user.get_followings()
    next = {
        "has_next":False,
        "page":0
    }
    query_post = Posts.query.order_by(Posts.created_at.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    print("has next",query_post.has_next)
    if query_post.has_next:
        next['has_next'] = True
        next['page'] = page + 1
    posts = []
    print(following_list)
    for post in query_post.items:
        print(post.user.id)
        if post.user.id in following_list or post.user.id == current_user.id:
            _hastag = []
            for hastag in post.hastags:
                _hastag.append(hastag.description)
            inloop_post = {
                "id": post.id,
                "content": post.content,
                "created_at": post.convert_to_local(),
                "author": post.user.username,
                "author_id": post.user.id,
                "hastags": _hastag,
                "like_state": post.check_like(current_user.id),
                "likes":post.get_user_like(),
                "comments": post.get_comments()
            }
            posts.append(inloop_post)
    # db.session.commit()
    return jsonify({
        "data_received":posts,
        "has_next": next['has_next'],
        "page": next['page']
    })

@posts_blueprint.route('/<id>', methods=["GET"])
@login_required
def get_post(id):
    query_post = Posts.query.filter_by(id = id).first()
    if query_post:
        return jsonify({
            "state":True,
            "id": query_post.id,
            "content": query_post.content,
            "created_at": query_post.convert_to_local(),
            "author": query_post.user.username,
            "author_id": query_post.user.id,
            "likes": query_post.get_user_like(),
            "comments": query_post.get_comments(),
            "like_state": query_post.check_like(current_user.id)
        })
    else:
        return jsonify({
            "state":False
        })


# like action
@posts_blueprint.route("/like/<id>", methods=["PUT","GET"])
@login_required
def post_like(id):
    post = Posts.query.filter_by(id = id).first()
    if post:
        post.likes.append(current_user)
        db.session.commit()
    else:
        print("post not found")
    return jsonify({
        "message":"like success",
        "length": post.get_like_number()
    })

@posts_blueprint.route("/unlike/<id>", methods=["DELETE","PUT"])
@login_required
def post_unlike(id):
    post = Posts.query.filter_by(id = id).first()
    if post:
        post.likes.remove(current_user)
        db.session.commit()
        return jsonify({
            "message":"unlike success",
            "length": post.get_like_number()
        })
    else:
        return jsonify({
            "message":"post not found"
        })

#comment section
@posts_blueprint.route("/<id>/create_comment", methods=["POST"])
@login_required
def create_comment(id):
    post = Posts.query.filter_by(id = id).first()
    if post:
        comment = Comment(author_id=current_user.id, content=request.json['content'])
        post.comments.append(comment)
        db.session.commit()
    return jsonify({
        "message":"created",
        "length":post.get_comments_number(),
        "comments":post.get_comments()
    })

@posts_blueprint.route("/<id>/comments", methods=["GET"])
@login_required
def get_comment(id):
    post = Posts.query.filter_by(id = id).first()
    if post:
        return jsonify({
            "state":True,
            "comments": post.get_comments()
        })


@posts_blueprint.route("/delete/<id>", methods={"DELETE"})
def delete_post(id):
    post = Posts.query.filter_by(id = id).first()
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({
            "message":"success"
        })
    else:
        return jsonify({
            "message": "there's no such a post"
        })

@posts_blueprint.route("/hastags", methods=["GET"])
@login_required
def get_most_popular():
    hastags_arr=[]
    top_hastags=[]
    all_hastags = Hastags.query.all()
    for tag in all_hastags:
        hastags_arr.append(tag.get_detail())
    all_hastag_sorted = sorted(hastags_arr, key = itemgetter('numb'), reverse=True)
    print(all_hastag_sorted)
    if len(all_hastag_sorted) >0:
        for i in range(0,3):
            if (i+1) < len(all_hastag_sorted):
                top_hastags.append(all_hastag_sorted[i])
    return jsonify({
        "message":"success",
        "data":top_hastags
    })

@posts_blueprint.route("/explore/page=<int:page>", methods=["GET"])
@login_required
def get_trending(page):
    trending = db.session.query(Posts).join((Hastags, Posts.hastags)).order_by(Posts.created_at.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    posts_ =[]
    for post in trending.items:
        posts_.append({
            "id": post.id,
            "content": post.content,
            "created_at": post.convert_to_local(),
            "author": post.user.username,
            "author_id": post.user.id,
            "likes": post.get_user_like(),
            "comments": post.get_comments(),
            "like_state": post.check_like(current_user.id)
        })

    next = {
        "has_next":False,
        "page":0
    }
    if trending.has_next:
        next['has_next'] = True
        next['page'] = page + 1
    return jsonify({
        "message":"success",
        "data":posts_,
        "has_next":next['has_next'],
        "page":next['page']
    })


@posts_blueprint.route("/trending/<tag>/page=<int:page>", methods=["GET"])
@login_required
def get_specific_trending(tag, page):
    tag= "#"+tag
    trending = db.session.query(Posts).join((Hastags, Posts.hastags)).filter(Hastags.description == tag).order_by(Posts.created_at.desc()).paginate(page, app.config['POST_PER_PAGE'], False)
    posts_ =[]
    for post in trending.items:
        posts_.append({
            "id": post.id,
            "content": post.content,
            "created_at": post.convert_to_local(),
            "author": post.user.username,
            "author_id": post.user.id,
            "likes": post.get_user_like(),
            "comments": post.get_comments(),
            "like_state": post.check_like(current_user.id)
        })

    next = {
        "has_next":False,
        "page":0
    }
    if trending.has_next:
        next['has_next'] = True
        next['page'] = page + 1
    return jsonify({
        "message":"success",
        "data":posts_,
        "has_next":next['has_next'],
        "page":next['page']
    })