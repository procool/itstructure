import time
import logging
import threading


import tornado.httpserver

from libs.server.tornado import TornadoDaemonBackend

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

def background(f):
    """
    a threading decorator
    use @background above the function you want to thread
    (run in the background)
    """
    def bg_f(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return bg_f



class TornadoHTTPDaemonServer(object):
    port = 5555 ## Default port
    host = None
    application = None


    def __init__(self, *args, **kwargs):
        self.is_exit = False
        super(TornadoHTTPDaemonServer, self).__init__(*args, **kwargs)


    def run(self):
        http_server = tornado.httpserver.HTTPServer(self.application)

        largs = {}
        if self.host is not None:
            largs['address'] = self.host
        http_server.listen(self.port, **largs)
        logging.info("Listen HTTP: %s:%s" % (self.host, self.port))

    def run_every_time(self):
        pass 

    def stop(self):
        self.is_exit = True



class TornadoHTTPDaemonBackend(TornadoDaemonBackend):


    def __init__(self, server):
        self.server_class = server

    @background
    def run_every_time(self):
        self.server.run_every_time()

    def run(self):

        self.server = self.server_class()
        self.server.run()

        self.run_every_time()

    def stop(self):
        self.server.stop()


