
from command import Command


class cmdQuit(Command):

    def make_answer(self, *args, **kwargs):
        self.client.server.is_exit = True
        return super(cmdQuit, self).make_answer(*args, **kwargs)

        
