import gevent

from commands import Commands as CommandsBase
class Commands(CommandsBase):
    @classmethod
    def process(cls, *args, **kwargs):
        gevent.spawn(super(Commands, cls).process, *args, **kwargs)
