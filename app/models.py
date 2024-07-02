# app/models.py
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.hash(password)

class BlogPost:
    def __init__(self, title, content, author, created_at=None):
        self.title = title
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now()

class Comment:
    def __init__(self, id, content, author, created_at=None):
        self.id = id
        self.content = content
        self.author = author
        self.created_at = created_at or datetime.now()
