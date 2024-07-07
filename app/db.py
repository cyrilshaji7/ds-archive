# app/db.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext

# Replace with your actual database URI
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Using bcrypt for hashing

# Define SQLAlchemy models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(50), nullable=False)
    password = Column(String(120), nullable=False)

class BlogPost(Base):
    __tablename__ = 'blog_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(1000), nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    post_id = Column(Integer, ForeignKey('blog_posts.id'))
    post = relationship("BlogPost", back_populates="comments")

BlogPost.comments = relationship("Comment", back_populates="post")

# Database class for interactions
class Database:
    def __init__(self):
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_user(self, email, username, password):
        hashed_password = pwd_context.hash(password)  # Hashing the password
        user = User(email=email, username=username, password=hashed_password)
        self.session.add(user)
        self.session.commit()

    def get_user(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def add_blog_post(self, title, content, author):
        blog_post = BlogPost(title=title, content=content, author=author)
        self.session.add(blog_post)
        self.session.commit()

    def get_all_blog_posts(self):
        return self.session.query(BlogPost).all()
    
    def get_post(self, post_id):
        return self.session.query(BlogPost).filter(BlogPost.id == post_id).one_or_none()

    def update_blog_post(self, post_id, title, content):
        post = self.get_post(post_id)
        if post:
            post.title = title
            post.content = content
            self.session.commit()
            return post
        return None

    def delete_comment(self, comment):
        self.session.delete(comment)
        self.session.commit()

    def add_comment(self, post_id, content, author):
        comment = Comment(content=content, author=author, post_id=post_id)
        self.session.add(comment)
        self.session.commit()

    def get_comment(self, post_id, comment_id):
        return self.session.query(Comment).filter_by(id=comment_id, post_id=post_id).one_or_none()
