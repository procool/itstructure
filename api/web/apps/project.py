import logging
from flaskcbv.core import engine
from flaskcbv.conf import settings
from flaskcbv.response import Response

from gsettings import settings as gsetts
from libs.server.bbclient import BBClient

application = engine.app
application.secret_key = 'lAiu,Wyta6M1!4$7J5Dptsm/Wo[S,R'


def page_not_found(e):
  return Response("""{"errno":-1,"error":"notfound","details":"undefined handler url"}""").render(), 404

application.register_error_handler(404, page_not_found)


## Connect to passport:
logging.error('Conecting to Blackbox...')
settings._BB_CLIENT = BBClient(gsetts.BLACKBOX_HOST, gsetts.BLACKBOX_PORT, do_reconnect=True, max_rate=100)
logging.error('Conected to Blackbox!')


