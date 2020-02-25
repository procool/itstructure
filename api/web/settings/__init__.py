import logging

FLASKCONFIG = 'flaskconfig'

APPLICATIONS = (
    'index', 'auth', 'collections_app',
)

DEFAULT_HEADERS = {
    'server' : 'DraftDesign API Server',
    'Access-Control-Allow-Origin': '*',
    ##'Access-Control-Allow-Credentials': 'false',
}

try:
    from local import *
except Exception as err:
    print "Local settings exception: %s" % err
    pass


