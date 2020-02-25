# -*- coding: utf-8 -*-
# vim: set expandtab shiftwidth=4:

__import__('gevent.monkey').monkey.patch_all()

import time
import logging
import threading
import socket
import gevent

from tornado.ioloop import IOLoop
from tornado.netutil import add_accept_handler
import tornado.iostream

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


class newConnection(object):
    stream_set = set([])

    def __init__(self, server, sock, address, data, commands=None):
        logging.debug('Receive a new data from UDP %s', address)
        self.server  = server
        self.socket  = sock
        self.address = address
        self.request = data

        if commands is not None:
            commands.process(self, data)

    def write(self, data, on_complete=None):
        self.socket.sendto(data, self.address)
        if on_complete is not None:
            try: on_complete()
            except: pass


class TornadoUDPDaemonServer(object):

    host = ""   ## Default host: 0.0.0.0
    port = 5555 ## Default port
    commands = None

    def __init__(self, io_loop=None, **kwargs):
        self.io_loop = io_loop or IOLoop.instance()
        self.is_exit = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.io_loop.add_handler(self.socket.fileno(), self.handle_stream, self.io_loop.READ)
        self.__bind((self.host, self.port))
        self.socket.setblocking(0)
        try: super(TornadoUDPDaemonServer, self).__init__(self, io_loop=self.io_loop, **kwargs)
        except: pass

    def handle_stream(self, fd, events):
        (data, source_ip_port) = self.socket.recvfrom(4096)

        newConnection(self, self.socket, source_ip_port, data, self.commands)





    def run_every_time(self):
        while True:
            if self.is_exit:
                break
            time.sleep(1)

    def stop(self):
        self.is_exit = True
        self.socket.close()

    def __bind(self, sockaddr):
        self.socket.bind(sockaddr)
        logging.info("Binding socket: %s" % ":".join(map(str, sockaddr)))



class TornadoUDPDaemonBackend(TornadoDaemonBackend):


    def __init__(self, server):
        self.server_class = server

    @background
    def run_every_time(self):
        self.server.run_every_time()
        try: return super(TornadoUDPDaemonBackend, self).run_every_time()
        except: pass

    def run(self):

        self.server = self.server_class()
        ##self.server.listen(self.server_class.port)

        self.run_every_time()



    def stop(self):
        self.server.stop()






