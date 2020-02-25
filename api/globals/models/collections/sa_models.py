from sqlalchemy import Table, MetaData, Column, Integer, VARCHAR, ForeignKey, DateTime, TEXT
from sqlalchemy import DECIMAL, Boolean,Float
from sqlalchemy.orm import mapper,relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false as sa_false
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_mptt.mixins import BaseNestedSets

from libs.db import get_metadata

metadata = get_metadata()

Base = declarative_base(metadata=metadata)


class Categories(Base, BaseNestedSets):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, nullable=False, unique=True)
    ident = Column(VARCHAR(50),  nullable=False, server_default='')
    name  = Column(VARCHAR(250), nullable=False, server_default='')
    comment = Column(VARCHAR(250), nullable=False, server_default='')
    description = Column(TEXT, nullable=False, server_default='')
    tags = Column(VARCHAR(250), nullable=False, server_default='')
    crdate = Column(DateTime(timezone=True), nullable=False, server_default=func.now())





class Objects(object):
    def __init__(self, cat_id):
        self.category_id = cat_id



objects = Table('objects', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, ),
    Column('ident', VARCHAR(50), nullable=False, server_default=''),
    Column('name', VARCHAR(250), nullable=False, server_default=''),
    Column('tags', VARCHAR(250), nullable=False, server_default=''),
    Column('comment', VARCHAR(250), nullable=False, server_default=''),
    Column('disabled', Boolean(), nullable=False, server_default=sa_false()),
    Column('extra', TEXT, nullable=False, server_default='{}'),

    ## extra_type: 0: json, 1: xml, 2: json gzipped, 3: xml gzipped
    Column('extra_type', Integer, nullable=False, server_default='0'),
    extend_existing=True,
)

mapper(Objects, objects, properties={
        'category': relationship(
                Categories, backref='main_objects',
                order_by=Categories.id,
        )
    },
    primary_key=[objects.c.id],
)





class ObjectsCategories(object):
    def __init__(self, obj_id, cat_id):
        self.category_id = cat_id
        self.object_id = obj_id

objects_categories = Table('objects_categories', metadata,
    Column('id', Integer, primary_key=True, nullable=False, unique=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, ),
    Column('object_id', Integer, ForeignKey('objects.id', ondelete='CASCADE'), nullable=False, ),
    Column('ident', VARCHAR(50), nullable=False, server_default=''),
    Column('name', VARCHAR(250), nullable=False, server_default=''),
    Column('tags', VARCHAR(250), nullable=False, server_default=''),
    Column('comment', VARCHAR(250), nullable=False, server_default=''),
    Column('disabled', Boolean(), nullable=False, server_default=sa_false()),
    Column('data', TEXT, nullable=True, server_default=''),
    Column('path', TEXT, nullable=True, server_default=''),
    Column('extra', TEXT, nullable=False, server_default='{}'),
    extend_existing=True,
)

mapper(ObjectsCategories, objects_categories, properties={
        'category': relationship(
                Categories, backref='objects',
                order_by=Categories.id,
        ),
        'object': relationship(
                Categories, backref='categories',
                order_by=Objects.id,
        ),
    },
    primary_key=[objects_categories.c.id],
)



