# -*- coding: utf-8 -*-
# vim: set expandtab shiftwidth=4:

__import__('gevent.monkey').monkey.patch_all()

import time
import logging
import threading

from tornado.ioloop import IOLoop

from libs.daemon.simpledaemon import SimpleDaemon


logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')


class TornadoDaemonBackend(object):

    def get_cli_args_names(self):
        return {
            'host': ['host', '--host', 'server host/ip address'],
            'port': ['port', '-p', '--port', 'server port'],
        }

    ## Add command line arguments:
    def set_cli_parser_args (self, parser, *args, **kwargs):
        host = self.get_cli_args_names()['host']
        port = self.get_cli_args_names()['port']
        parser.add_argument(*host[1:-1], help=host[-1])
        parser.add_argument(*port[1:-1], help=port[-1], type=int)


    ## Process command line arguments by namespace:
    def cli_process_args(self, namespace, *args, **kwargs):
        self.server_class.backend = self
        host = self.get_cli_args_names()['host'][0]
        port = self.get_cli_args_names()['port'][0]

        if getattr(namespace, host) is not None:
            self.server_class.host = getattr(namespace, host)

        if getattr(namespace, port) is not None:
            self.server_class.port = getattr(namespace, port)




class TornadoDaemon(SimpleDaemon):

    __servers = []

    def __init__(self, servers=[], **kwargs):
        self.servers  = servers

        for server in self.servers:   
            ## Making backends instances:
            self.__servers.append( server[0](server[1]) )

        return super(TornadoDaemon, self).__init__(**kwargs)


    def sig_handler(self, sig_num, frame):
        for server in self.__servers:
            server.stop()
        try: IOLoop.instance().stop()
        except: pass
        return super(TornadoDaemon, self).sig_handler(sig_num, frame)

    def run_after(self, backends):
        pass

    def get_backends(self):
        return self.__servers

    def run(self):

        super(TornadoDaemon, self).run()

        for server in self.__servers:
            ## Starting servers:
            server.run()

        self.run_after(self.__servers)
        for backend in self.__servers:
            backend.daemon = self

        IOLoop.instance().start()



    ###### Command line arguments processing: ################
    ## Next methods will be execute after __init__, on .cli()

    ## Add command line arguments:
    def set_cli_parser_args (self, parser, *args, **kwargs):
        for backend in self.__servers:
            try: backend.set_cli_parser_args(parser, *args, **kwargs)
            except: pass
        return super(TornadoDaemon, self).set_cli_parser_args(parser, *args, **kwargs)


    ## Process command line arguments by namespace:
    def cli_process_args(self, namespace, *args, **kwargs):
        for backend in self.__servers:
            try: backend.cli_process_args(namespace, *args, **kwargs)
            except: pass
        return super(TornadoDaemon, self).cli_process_args(namespace, *args, **kwargs)




if __name__ == "__main__":
    daemon = TornadoDaemon()
    daemon.cli()

