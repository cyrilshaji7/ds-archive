"""Alter content column to Text

Revision ID: 47dc1825d9be
Revises: dad50979faad
Create Date: 2024-07-31 16:45:15.774391

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = '47dc1825d9be'  # Replace with your revision ID
down_revision = 'dad50979faad'  # Replace with the previous revision ID
branch_labels = None
depends_on = None

def upgrade():
    # Create a new table with the updated schema
    op.create_table(
        'blog_posts_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text, nullable=False),  # Updated type
        sa.Column('author', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('featured_image', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True)
    )
    
    # Copy data from the old table to the new table
    op.execute("""
        INSERT INTO blog_posts_new (id, title, content, author, created_at, featured_image, category)
        SELECT id, title, content, author, created_at, featured_image, category
        FROM blog_posts
    """)
    
    # Drop the old table
    op.drop_table('blog_posts')
    
    # Rename the new table to the old table's name
    op.rename_table('blog_posts_new', 'blog_posts')

def downgrade():
    # Reverse the upgrade changes if needed
    op.create_table(
        'blog_posts_old',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('content', sa.String(length=1000), nullable=False),  # Old type
        sa.Column('author', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('featured_image', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True)
    )
    
    # Copy data back to the old table
    op.execute("""
        INSERT INTO blog_posts_old (id, title, content, author, created_at, featured_image, category)
        SELECT id, title, content, author, created_at, featured_image, category
        FROM blog_posts
    """)
    
    # Drop the current table
    op.drop_table('blog_posts')
    
    # Rename the old table back to the original name
    op.rename_table('blog_posts_old', 'blog_posts')
