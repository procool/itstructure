import argparse
import sys
import signal

from basedaemon import BaseDaemon

class SimpleDaemon(BaseDaemon):

    logfile = None
    pidfile = "%s.pid"
    pid_rm_on_stop = False

    def __init__(self, pidfile=None, *args, **kwargs):
        self.pidfile = self.pidfile % sys.argv[0]
        if pidfile is not None:
            self.pidfile = pidfile

        return super(SimpleDaemon, self).__init__(*args, **kwargs)

    def usage(self):
        return "Usage: %s start|stop|restart" % sys.argv[0]


    def sig_handler(self, sig_num, frame):
        try: self.proc.kill()
        except: sys.exit(0)

    def set_signals(self):
        signal.signal(signal.SIGINT,  self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGQUIT, self.sig_handler)

    def run(self):
        self.set_signals()

    ## Add command line arguments:
    def set_cli_parser_args (self, parser, *args, **kwargs):
        parser.add_argument ('--pid', help="path to daemon pidfile" )
        parser.add_argument ('--log', help="path to daemon log" )
        parser.add_argument ('action', choices=['start', 'stop', 'restart', 'interactive',], )
        
    ## Returns command line arguments parser:
    def get_cli_parser (self, *args, **kwargs):
        return argparse.ArgumentParser(*args, **kwargs)

    ## Returns namespase of parsed command line:
    def cli_parse_argv (self, argv, *args, **kwargs):
        parser = self.get_cli_parser()
        self.set_cli_parser_args(parser)
        return parser.parse_args(argv)
    
    ## Process command line arguments by namespace:
    def cli_process_args(self, namespace, *args, **kwargs):

        if namespace.pid is not None:
            self.pidfile = namespace.pid

        if namespace.log is not None:
            self.logfile = namespace.log
        else:
            self.stdout = sys.stdout
            self.stderr = sys.stderr


    def cli(self):

        namespace = self.cli_parse_argv(sys.argv[1:])
        self.cli_process_args(namespace)


        if namespace.action == 'interactive':
            self.pid = ''
            self.run()
        elif namespace.action == 'start':
            self.start()
        elif namespace.action == 'stop':
            self.stop()
        elif namespace.action == 'restart':
            self.restart()
        else:
            print "Unknown command"
            sys.exit(2)


