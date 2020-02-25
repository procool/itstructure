import os
from flaskcbv.conf import settings

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True

SQLALCHEMY_POOL_SIZE=2
SQLALCHEMY_ECHO=False
#SQLALCHEMY_ECHO=True


