
from command import Command


class cmdEcho(Command):

    def make_answer(self, *args, **kwargs):
        answer = super(cmdEcho, self).make_answer(*args, **kwargs)
        answer.update(self.request)
        return answer

        
