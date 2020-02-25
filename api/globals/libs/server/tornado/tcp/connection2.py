import logging

from tornado import gen

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


## New connection activity:
class newConnection(object):

    stream_set = set([])

    def __init__(self, server, stream, address, commands=None, onclose=None):
        logger.info('Receive a new connection from %s', address)
        self.server = server
        self.stream = stream
        self.address = address
        self.onclose = onclose
        self.commands = commands
        self.stream_set.add(self.stream)
        self.stream.set_close_callback(self._on_close)

    @gen.coroutine
    def run(self):
        self.read_message_wrapper()

    def read_message_wrapper(self):
        logger.debug('start reading wrapper...')
        while True:
            if self.stream.reading():
                break
            r = self.read_message()
            if r is not None:
                break

    def read_message(self):
        logger.debug('start reading...')
        r = self.stream.read_until('\n', self._on_read_line)
        logger.debug('reading complete! %s' % r)
        return r


    def _on_read_line(self, data):
        logger.debug('Command from %s: %s' % (self.address, data))

        if self.commands is not None:
            self.commands.process(self, data)
        self.read_message_wrapper()


    ## Write answer complete:
    def _on_write_complete(self, *args, **kwargs):
        logger.debug('Write answer to %s: %s' % (self.address, args))

    def _on_close(self):
        logger.info('client quit %s', self.address)
        if self.onclose is not None:
            self.onclose(self)
        self.stream_set.remove(self.stream)

    @gen.coroutine
    def write(self, data, on_complete=None):
        yield self.stream.write(data, on_complete)


