from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token as jwt_create_access_token, jwt_required, get_jwt_identity
from passlib.context import CryptContext
from datetime import timedelta, datetime

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this in production
jwt = JWTManager(app)

# Sample user database (replace with database integration)
fake_users_db = {
    "user1@example.com": {
        "username": "user1",
        "password": "$2b$12$Qq/vcGKnojLpsB2xW0Vlde9hZG9ERW2h8jBW6sOLwS4JxvYy5Ld92"  # Password: password123
    }
}

# Sample blog posts database (replace with database integration)
fake_blog_posts_db = []
fake_comments_db = {}
# Password hashing helper
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model for registration
class UserCreate:
    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.hash(password)

# User model for login
class UserLogin:
    def __init__(self, email, password):
        self.email = email
        self.password = password

# JWT token helper function
def create_access_token(identity):
    expires = timedelta(minutes=30)
    return jwt_create_access_token(identity=identity, expires_delta=expires)

# Endpoint for user registration
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email in fake_users_db:
        return jsonify({"message": "User already exists"}), 400

    user = UserCreate(email=email, password=password)
    fake_users_db[email] = {"username": email.split("@")[0], "password": user.password}
    return jsonify({"message": "User created successfully"}), 201

# Endpoint for user login and token generation
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if email not in fake_users_db:
        return jsonify({"message": "User not found"}), 404

    user = fake_users_db[email]
    if not pwd_context.verify(password, user["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    return jsonify({"access_token": access_token}), 200

# Endpoint for creating blog posts (requires authentication)
@app.route("/api/posts/create", methods=["POST"])
@jwt_required()
def create_blog_post():
    current_user = get_jwt_identity()
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    new_post = {
        "title": title,
        "content": content,
        "author": current_user,
        "created_at": str(datetime.now()),
    }
    fake_blog_posts_db.append(new_post)
    return jsonify({"message": "Blog post created successfully"}), 201

# Endpoint for retrieving all blog posts (no authentication required)
@app.route("/api/posts", methods=["GET"])
def get_blog_posts():
    return jsonify(fake_blog_posts_db), 200

# Endpoint for retrieving comments of a blog post (no authentication required)
@app.route("/api/posts/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    if post_id not in fake_comments_db:
        return jsonify({"message": "No comments found for this post"}), 404

    return jsonify(fake_comments_db[post_id]), 200

# Endpoint for adding a comment to a blog post (requires authentication)
@app.route("/api/posts/<int:post_id>/comments/create", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    current_user = get_jwt_identity()
    data = request.get_json()
    content = data.get("content")

    new_comment = {
        "id": len(fake_comments_db.get(post_id, [])) + 1,  # Auto-incremented ID (for demo purposes)
        "content": content,
        "author": current_user,
        "created_at": str(datetime.now()),
    }

    if post_id not in fake_comments_db:
        fake_comments_db[post_id] = []

    fake_comments_db[post_id].append(new_comment)
    return jsonify({"message": "Comment added successfully"}), 201

if __name__ == "__main__":
    app.run(debug=True)
