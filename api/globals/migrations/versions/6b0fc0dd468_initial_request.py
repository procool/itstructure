"""initial request

Revision ID: 6b0fc0dd468
Revises: None
Create Date: 2019-06-23 05:08:06.785823

"""

# revision identifiers, used by Alembic.
revision = '6b0fc0dd468'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ident', sa.VARCHAR(length=50), server_default='', nullable=False),
    sa.Column('name', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('description', sa.TEXT(), server_default='', nullable=False),
    sa.Column('tags', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('crdate', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layouts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('prototypes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('description', sa.TEXT(), server_default='', nullable=False),
    sa.Column('lastupdate', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layout_discuss',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layout_id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('crdate', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=False),
    sa.Column('lastupdate', sa.DateTime(timezone=True), nullable=False),
    sa.Column('content', sa.TEXT(), server_default='', nullable=False),
    sa.Column('setts', sa.TEXT(), server_default='{}', nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('user_name', sa.VARCHAR(length=250), nullable=True),
    sa.Column('is_read', sa.Boolean(), server_default=sa.text(u'false'), nullable=False),
    sa.ForeignKeyConstraint(['layout_id'], ['layouts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_id'], ['layout_discuss.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layout_discuss_objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layout_discuss_id', sa.Integer(), nullable=False),
    sa.Column('prototype_id', sa.Integer(), nullable=False),
    sa.Column('extra', sa.VARCHAR(length=250), server_default='{}', nullable=False),
    sa.ForeignKeyConstraint(['layout_discuss_id'], ['layouts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prototype_id'], ['prototypes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layout_protos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layout_id', sa.Integer(), nullable=False),
    sa.Column('prototype_id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.ForeignKeyConstraint(['layout_id'], ['layouts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prototype_id'], ['prototypes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('ident', sa.VARCHAR(length=50), server_default='', nullable=False),
    sa.Column('name', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('tags', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('disabled', sa.Boolean(), server_default=sa.text(u'false'), nullable=False),
    sa.Column('extra', sa.TEXT(), server_default='{}', nullable=False),
    sa.Column('extra_type', sa.Integer(), server_default='0', nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('objects_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('ident', sa.VARCHAR(length=50), server_default='', nullable=False),
    sa.Column('name', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('tags', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('disabled', sa.Boolean(), server_default=sa.text(u'false'), nullable=False),
    sa.Column('data', sa.TEXT(), server_default='', nullable=True),
    sa.Column('path', sa.TEXT(), server_default='', nullable=True),
    sa.Column('extra', sa.TEXT(), server_default='{}', nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['object_id'], ['categories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('proto_objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('object_id', sa.Integer(), nullable=False),
    sa.Column('prototype_id', sa.Integer(), nullable=False),
    sa.Column('layer', sa.Integer(), server_default='0', nullable=True),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.Column('extra', sa.TEXT(), server_default='{}', nullable=False),
    sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['parent_id'], ['proto_objects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['prototype_id'], ['prototypes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layout_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('layout_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('comment', sa.VARCHAR(length=250), server_default='', nullable=False),
    sa.ForeignKeyConstraint(['layout_id'], ['proto_objects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('layout_users_access',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('access', sa.VARCHAR(length=32), server_default='', nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['layout_users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('layout_users_access')
    op.drop_table('layout_users')
    op.drop_table('proto_objects')
    op.drop_table('objects_categories')
    op.drop_table('objects')
    op.drop_table('layout_protos')
    op.drop_table('layout_discuss_objects')
    op.drop_table('layout_discuss')
    op.drop_table('prototypes')
    op.drop_table('layouts')
    op.drop_table('categories')
    ### end Alembic commands ###