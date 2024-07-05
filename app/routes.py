from flask import Blueprint, jsonify, request, render_template, redirect, url_for, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, decode_token
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models import User, BlogPost, Comment
from app.db import Database

api = Blueprint('api', __name__, url_prefix='/api')  # Specify url_prefix='/api' for the Blueprint
db = Database()

# JWT configuration
jwt = JWTManager()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user['email']

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.get_user(identity)

# Endpoint to render index.html
@api.route("/", methods=["GET"])
def index():
    current_user = None
    access = None
    try:
        access = request.cookies['access_token']
        print(access)
        decoded = decode_token(access)
        current_user = decoded['sub']
    except Exception as e:
        print(f"Error getting user identity: {e}")
    print(current_user)
    posts = db.get_all_blog_posts()
    return render_template("index.html", posts=posts, user=current_user, access_token=access)

# Endpoint to render login.html
@api.route("/login", methods=["GET", "POST"])
def login():
    access_token = None
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")
        user = db.get_user(email=email)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if not pwd_context.verify(password, user.password):
            return jsonify({"message": "Invalid credentials"}), 401

        access_token = create_access_token(identity=email)
        print(access_token)
        response = redirect(url_for('api.index'))
        response.set_cookie('access_token', access_token, httponly=False)  # httponly wasted 4 hours of my life >:(
        return response

    return render_template("login.html")

@api.route("/logout", methods=['POST', 'GET'])
def logout():
    response = make_response(redirect(url_for('api.index')))
    response.set_cookie('access_token', '', expires=0)
    return response

# Endpoint to render register.html
@api.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")

        if db.get_user(email):
            return jsonify({"message": "User already exists"}), 400

        db.add_user(email=email, username=email.split("@")[0], password=password)
        return redirect(url_for('api.login'))  # Redirect to login page after successful registration
    return render_template("register.html")

# Endpoint to render blog.html for creating and viewing blog posts
@api.route("/posts", methods=["GET"])
def get_blog_posts():
    posts = db.get_all_blog_posts()
    return render_template("blog.html", posts=posts)

# Endpoint to handle creating blog posts
@api.route("/posts/create", methods=["GET", "POST"])
@jwt_required()
def create_blog_post():
    print("asdfsdfsdfsdf")
    current_user = get_jwt_identity()
    
    print(current_user)
    if request.method == 'GET':
        return render_template('create_post.html', user=current_user)
    
    print(f"The token is {current_user}")
    if request.method == "POST":
        # token = request.cookies['access_token']
        # print(token)
        # if not token:
        #     return jsonify({"message": "Missing access token"}), 401

        current_user = get_jwt_identity()
        data = request.form
        print(data)
        # title = data.get("title")
        # content = data.get("content")
        title = "dasfdf"
        content = "Fsdfsdfsdf"
        db.add_blog_post(title=title, content=content, author=current_user)
        return redirect(url_for('api.get_blog_posts'))
    #return jsonify(logged_in_as=current_user), 200
    return render_template("create_post.html")

# Endpoint to handle retrieving comments for a blog post
@api.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    comments = db.get_comments_for_post(post_id)
    if not comments:
        return jsonify({"message": "No comments found for this post"}), 404
    return jsonify([{"id": comment.id, "content": comment.content, "author": comment.author, "created_at": comment.created_at} for comment in comments]), 200

# Endpoint to handle adding comments to a blog post
@api.route("/posts/<int:post_id>/comments/create", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    current_user = get_jwt_identity()
    data = request.form
    content = data.get("content")

    new_comment = Comment(id=len(db.get_comments_for_post(post_id)) + 1, content=content, author=current_user)
    db.add_comment(post_id=post_id, content=content, author=current_user)
    return jsonify({"message": "Comment added successfully"}), 201


@api.route('/test', methods=['GET', 'POST'])
@jwt_required()
def testing():
    users = get_jwt_identity()
    return jsonify({"user data:": users})