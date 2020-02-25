from sqlalchemy import Table, MetaData, Column, Integer, VARCHAR, ForeignKey, TEXT, DateTime
from sqlalchemy import DECIMAL, Boolean,Float
from sqlalchemy.orm import mapper,relationship
from sqlalchemy.sql.expression import false as sa_false
from sqlalchemy.sql import func

from libs.db import get_metadata
from models.collections.sa_models import Objects, objects

metadata = get_metadata()


class Prototypes(object):
    def __init__(self):
        pass

prototypes = Table('prototypes', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('name', VARCHAR(100), nullable=False),
    Column('description', TEXT, nullable=False, server_default=''),
    Column('lastupdate', DateTime(timezone=True), nullable=False),
    extend_existing=True,
)

mapper(Prototypes, prototypes, properties={
    },
    primary_key=[prototypes.c.id],
)




class ProtoObjects(object):
    def __init__(self, proto_id, oid, parent_id=None):
        self.prototype_id = proto_id
        self.object_id = oid
        self.parent_id = parent_id



proto_objects = Table('proto_objects', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('parent_id', Integer, ForeignKey('proto_objects.id', ondelete='CASCADE'), nullable=True, ),
    Column('object_id', Integer, ForeignKey('objects.id', ondelete='CASCADE'), nullable=False, ),
    Column('prototype_id', Integer, ForeignKey('prototypes.id', ondelete='CASCADE'), nullable=False, ),
    Column('layer', Integer, server_default='0'),
    Column('comment', VARCHAR(250), nullable=False, server_default=''),
    Column('extra', TEXT, nullable=False, server_default='{}'),
    extend_existing=True,
)


mapper(ProtoObjects, proto_objects, properties={
        'parent': relationship(
                ProtoObjects, backref='children',
                cascade='all,delete,delete-orphan',
                single_parent=True,
                remote_side=proto_objects.c.id,
        ),
        'object': relationship(
                Objects, backref='proto_objects',
                order_by=Objects.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
        'prototype': relationship(
                Prototypes, backref='proto_objects',
                order_by=Prototypes.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
    },
    primary_key=[proto_objects.c.id],
)





class Layouts(object):
    def __init__(self):
        pass

layouts = Table('layouts', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    extend_existing=True,
)

mapper(Layouts, layouts, properties={
    },
    primary_key=[layouts.c.id],
)





class LayoutProtos(object):
    def __init__(self):
        pass

layout_protos = Table('layout_protos', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('layout_id', Integer, ForeignKey('layouts.id', ondelete='CASCADE'), nullable=False, ),
    Column('prototype_id', Integer, ForeignKey('prototypes.id', ondelete='CASCADE'), nullable=False, ),
    Column('comment', VARCHAR(250), nullable=False, server_default=''),
    extend_existing=True,
)

mapper(LayoutProtos, layout_protos, properties={
        'layout': relationship(
                Layouts, backref='protos',
                order_by=Layouts.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
        'prototype': relationship(
                Prototypes, backref='layouts',
                order_by=Prototypes.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
    },
    primary_key=[layout_protos.c.id],
)





class LayoutDiscuss(object):
    def __init__(self):
        pass

layout_discuss = Table('layout_discuss', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('layout_id', Integer, ForeignKey('layouts.id', ondelete='CASCADE'), nullable=False, ),
    Column('parent_id', Integer, ForeignKey('layout_discuss.id', ondelete='SET NULL'), nullable=True, ),
    Column('crdate', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column('lastupdate', DateTime(timezone=True), nullable=False),
    Column('content', TEXT, nullable=False, server_default=''),
    Column('setts', TEXT, nullable=False, server_default='{}'),
    Column('user_id', Integer, nullable=True),
    Column('user_name', VARCHAR(250), nullable=True),
    Column('is_read', Boolean(), nullable=False, server_default=sa_false()),
    extend_existing=True,
)

mapper(LayoutDiscuss, layout_discuss, properties={
        'layout': relationship(
                Layouts, backref='discussions',
                order_by=Layouts.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
        'parent': relationship(
                LayoutDiscuss, backref='children',
                cascade='all,delete,delete-orphan',
                single_parent=True,
                remote_side=layout_discuss.c.id,
        ),
    },
    primary_key=[layout_discuss.c.id],
)


class LayoutDiscussObjects(object):
    def __init__(self):
        pass

layout_discuss_objects = Table('layout_discuss_objects', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('layout_discuss_id', Integer, ForeignKey('layout_discuss.id', ondelete='CASCADE'), nullable=False, ),
    Column('prototype_id', Integer, ForeignKey('prototypes.id', ondelete='CASCADE'), nullable=False, ),
    Column('extra', VARCHAR(250), nullable=False, server_default='{}'),
    extend_existing=True,
)

mapper(LayoutDiscussObjects, layout_discuss_objects, properties={
        'layout_discuss': relationship(
                LayoutDiscuss, backref='objects',
                order_by=LayoutDiscuss.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
        'prototype': relationship(
                Prototypes, backref='discussions',
                order_by=Prototypes.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
    },
    primary_key=[layout_discuss_objects.c.id],
)





class LayoutUsers(object):
    def __init__(self):
        pass

layout_users = Table('layout_users', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('layout_id', Integer, ForeignKey('layouts.id', ondelete='CASCADE'), nullable=False, ),
    Column('user_id', Integer, nullable=False, ),
    Column('comment', VARCHAR(250), nullable=False, server_default=''),
    extend_existing=True,
)

mapper(LayoutUsers, layout_users, properties={
        'layout': relationship(
                Layouts, backref='users',
                order_by=Layouts.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
    },
    primary_key=[layout_users.c.id],
)


class LayoutUsersAccess(object):
    def __init__(self):
        pass

layout_users_access = Table('layout_users_access', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('user_id', Integer, ForeignKey('layout_users.id', ondelete='CASCADE'), nullable=False, ),
    Column('access', VARCHAR(32), nullable=False, server_default=''),
    extend_existing=True,
)

mapper(LayoutUsersAccess, layout_users_access, properties={
        'user': relationship(
                LayoutUsers, backref='access',
                order_by=LayoutUsers.id,
                cascade='all,delete,delete-orphan',
                single_parent=True,
        ),
    },
    primary_key=[layout_users_access.c.id],
)




