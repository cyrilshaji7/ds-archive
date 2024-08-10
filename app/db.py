import os
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import Table, MetaData

# Read the database URI from environment variable
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/defaultdb')

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Using bcrypt for hashing

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
    content = Column(Text, nullable=False)  # Changed to Text for larger content
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    featured_image = Column(String(255))  # For image URLs
    category = Column(String(50))
    
    # Relationship with comments
    comments = relationship('Comment', back_populates='post')
    tags = relationship('Tag', secondary='post_tags', back_populates='posts')

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(String(255), nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    post_id = Column(Integer, ForeignKey('blog_posts.id'))
    parent_comment_id = Column(Integer, ForeignKey('comments.id'))

    # Define relationship for replies
    replies = relationship('Comment', 
                           cascade='all, delete-orphan', 
                           backref=backref('parent', remote_side=[id], uselist=False), 
                           remote_side=[parent_comment_id],
                           lazy=True)

    # Define relationship with BlogPost
    post = relationship('BlogPost', back_populates='comments')

# Association Table for many-to-many relationship between BlogPost and Tag
post_tags = Table('post_tags', Base.metadata,
    Column('post_id', Integer, ForeignKey('blog_posts.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    posts = relationship('BlogPost', secondary=post_tags, back_populates='tags')


# Define Database class for interactions
class Database:
    def __init__(self):
        engine = create_engine(SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def add_user(self, email, username, password):
        hashed_password = pwd_context.hash(password)
        user = User(email=email, username=username, password=hashed_password)
        self.session.add(user)
        self.session.commit()

    def get_user(self, email):
        return self.session.query(User).filter_by(email=email).first()

    def add_blog_post(self, title, content, author, featured_image=None, category=None, tags=[]):
        blog_post = BlogPost(title=title, content=content, author=author, featured_image=featured_image, category=category)
        # Add tags to the post
        for tag_name in tags:
            tag = self.session.query(Tag).filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                self.session.add(tag)
            blog_post.tags.append(tag)
        self.session.add(blog_post)
        self.session.commit()

    def get_all_blog_posts(self):
        return self.session.query(BlogPost).all()
    
    def get_post(self, post_id):
        return self.session.query(BlogPost).filter_by(id=post_id).one_or_none()

    def update_blog_post(self, post_id, title, content, featured_image=None, category=None):
        post = self.get_post(post_id)
        if post:
            post.title = title
            post.content = content
            post.featured_image = featured_image
            post.category = category
            self.session.commit()
            return post
        return None

    def delete_blog_post(self, post_id):
        post = self.get_post(post_id)
        if post:
            self.session.delete(post)
            self.session.commit()
            return True
        return False

    def add_comment(self, post_id, content, author, parent_comment_id=None):
        comment = Comment(content=content, author=author, post_id=post_id, parent_comment_id=parent_comment_id)
        self.session.add(comment)
        self.session.commit()

    def get_comments_for_post(self, post_id):
        return self.session.query(Comment).filter_by(post_id=post_id, parent_comment_id=None).all()

    def get_replies_for_comment(self, comment_id):
        return self.session.query(Comment).filter_by(parent_comment_id=comment_id).all()

    def get_comment(self, post_id, comment_id):
        return self.session.query(Comment).filter_by(id=comment_id, post_id=post_id).one_or_none()

    def delete_comment(self, comment):
        if not isinstance(comment, Comment):
            comment = self.session.query(Comment).filter_by(id=comment).first()
        if comment:
            self.session.delete(comment)
            self.session.commit()
            return True
        return False
