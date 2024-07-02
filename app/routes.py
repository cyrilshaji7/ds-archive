# app/routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models import User, BlogPost, Comment
from app.db import Database

api = Blueprint('api', __name__)
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

# Endpoint for user registration
@api.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if db.get_user(email):
        return jsonify({"message": "User already exists"}), 400

    db.add_user(email=email, username=email.split("@")[0], password=password)
    return jsonify({"message": "User created successfully"}), 201

# Endpoint for user login and token generation
@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = db.get_user(email=email)  # Assuming db.get_user() retrieves User object

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not pwd_context.verify(password, user.password):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    return jsonify({"access_token": access_token}), 200

# Endpoint for creating blog posts (requires authentication)
@api.route("/posts/create", methods=["POST"])
@jwt_required()
def create_blog_post():
    current_user = get_jwt_identity()
    
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    print(title, content, current_user)
    new_post = BlogPost(title=title, content=content, author=current_user)
    db.add_blog_post(title=title, content=content, author=current_user)
    return jsonify({"message": "Blog post created successfully"}), 201

# Endpoint for retrieving all blog posts (no authentication required)
@api.route("/posts", methods=["GET"])
def get_blog_posts():
    posts = db.get_all_blog_posts()
    return jsonify([{"title": post.title, "content": post.content, "author": post.author, "created_at": post.created_at} for post in posts]), 200

# Endpoint for retrieving comments of a blog post (no authentication required)
@api.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    comments = db.get_comments_for_post(post_id)
    if not comments:
        return jsonify({"message": "No comments found for this post"}), 404
    return jsonify([{"id": comment.id, "content": comment.content, "author": comment.author, "created_at": comment.created_at} for comment in comments]), 200

# Endpoint for adding a comment to a blog post (requires authentication)
@api.route("/posts/<int:post_id>/comments/create", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    content = data.get("content")

    new_comment = Comment(id=len(db.get_comments_for_post(post_id)) + 1, content=content, author=current_user)
    db.add_comment(post_id, new_comment, author=current_user)
    return jsonify({"message": "Comment added successfully"}), 201
