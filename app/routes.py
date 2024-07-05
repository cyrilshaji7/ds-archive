from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session
from datetime import timedelta
from passlib.context import CryptContext
from app.models import User, BlogPost, Comment
from app.db import Database

api = Blueprint('api', __name__, url_prefix='/api')  # Specify url_prefix='/api' for the Blueprint
db = Database()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoint to render index.html
@api.route("/", methods=["GET"])
def index():
    current_user = session.get('user_email')
    access_token = session.get('access_token')
    posts = db.get_all_blog_posts()
    return render_template("index.html", posts=posts, user=current_user, access_token=access_token)

# Endpoint to render login.html
@api.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        email = data.get("email")
        password = data.get("password")
        user = db.get_user(email=email)
        if not user:
            return jsonify({"message": "User not found"}), 404

        if not pwd_context.verify(password, user.password):
            return jsonify({"message": "Invalid credentials"}), 401

        # Store user email in session
        session['user_email'] = email
        return redirect(url_for('api.index'))

    return render_template("login.html")

@api.route("/logout", methods=['POST', 'GET'])
def logout():
    session.pop('user_email', None)
    session.pop('access_token', None)
    return redirect(url_for('api.index'))

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
def create_blog_post():
    if request.method == 'GET':
        current_user = session.get('user_email')
        return render_template('create_post.html', user=current_user)

    if request.method == "POST":
        current_user = session.get('user_email')
        data = request.form
        title = data.get("title")
        content = data.get("content")
        db.add_blog_post(title=title, content=content, author=current_user)
        return redirect(url_for('api.index'))

    return render_template("index.html")

# Endpoint to handle retrieving comments for a blog post
@api.route("/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    comments = db.get_comments_for_post(post_id)
    if not comments:
        return jsonify({"message": "No comments found for this post"}), 404
    return jsonify([{"id": comment.id, "content": comment.content, "author": comment.author, "created_at": comment.created_at} for comment in comments]), 200

# Endpoint to handle adding comments to a blog post
@api.route("/posts/<int:post_id>/comments/create", methods=["POST"])
def add_comment(post_id):
    current_user = session.get('user_email')
    data = request.form
    content = data.get("content")
    db.add_comment(post_id=post_id, content=content, author=current_user)
    return jsonify({"message": "Comment added successfully"}), 201

# Test endpoint to check current session user
@api.route('/test', methods=['GET', 'POST'])
def testing():
    current_user = session.get('user_email')
    return jsonify({"user data:": current_user})