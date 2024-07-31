from flask import Blueprint, jsonify, request, render_template, redirect, url_for, session, abort, flash
from passlib.context import CryptContext
import markdown
from app.db import Database

api = Blueprint('api', __name__)  # Specify url_prefix='/api' for the Blueprint
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
        featured_image = data.get("featured_image")
        category = data.get("category")
        tags = data.getlist("tags[]")
        db.add_blog_post(title=title, content=content, author=current_user, featured_image=featured_image, category=category, tags=tags)
        return redirect(url_for('api.index'))

    return render_template("index.html")


@api.route("/posts/<int:post_id>", methods=['GET'])
def get_post(post_id):
    if request.method=='GET':
        current_user = session.get('user_email')
        post = db.get_post(post_id)
        if post:
            post_content_html = markdown.markdown(post.content)
            print(post_content_html)
            return render_template('post.html', post=post, user=current_user, post_content_html=post_content_html)
        else:
            return render_template('error.html')

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
    if not current_user:
        abort(403)  # Unauthorized if user is not logged in
    
    content = request.form.get("content")
    parent_comment_id = request.form.get("parent_comment_id")
    
    try:
        if parent_comment_id:
            db.add_comment(post_id=post_id, content=content, author=current_user, parent_comment_id=parent_comment_id)
        else:
            db.add_comment(post_id=post_id, content=content, author=current_user)
        
        flash('Comment added successfully!', 'success')
        return redirect(url_for('api.get_post', post_id=post_id))
    except Exception as e:
        flash(f'Failed to add comment: {str(e)}', 'error')
        return redirect(url_for('api.get_post', post_id=post_id))


# New function to delete a post
@api.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    current_user = session.get('user_email')
    post = db.get_post(post_id)
    if post.author != current_user:
        return jsonify({"message": "Unauthorized action"}), 403
    db.delete_blog_post(post_id)
    return redirect(url_for('api.index'))

# New function to delete a comment
@api.route("/posts/<int:post_id>/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(post_id, comment_id):
    current_user = session.get('user_email')
    comment = db.get_comment(post_id, comment_id)

    if not comment or comment.author != current_user:
        return jsonify({"message": "Unauthorized"}), 403

    db.delete_comment(comment)
    return redirect(url_for('api.get_post', post_id=post_id)) 

# New function to edit a post
@api.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    current_user = session.get('user_email')
    post = db.get_post(post_id)
    if post.author != current_user:
        return jsonify({"message": "Unauthorized action"}), 403

    if request.method == 'GET':
        return render_template('edit_post.html', post=post, user=current_user)

    if request.method == "POST":
        data = request.form
        title = data.get("title")
        content = data.get("content")
        db.update_blog_post(post_id, title=title, content=content)
        return redirect(url_for('api.get_post', post_id=post_id))

    return render_template("index.html")