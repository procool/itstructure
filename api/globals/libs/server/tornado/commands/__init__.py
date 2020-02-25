import json

from echo import cmdEcho
from quit import cmdQuit

class Commands(object):

    @classmethod
    def get_commands(cls):
        return {
            'echo' : cmdEcho,
            'quit' : cmdQuit,
        }

    ## Make answer as JSON with errors:
    @staticmethod
    def json_answer(data={}):
        answ = {
            'errno'   : 0,
            'error'   : 'Ok',
            'details' : '',
        }
        if not data is None:
            answ.update(data)
        #logging.debug('DEBUG001: %s', answ)
        return json.dumps(answ) + '\r\n'



    ## Process incomming command:
    @classmethod
    def process(cls, client, data):
        try:
            data = json.loads(data)
        except Exception as err:
            cls.answer(client, cls.json_answer({
                'errno': -1,
                'error': err.message
            }))
            return None

        if not 'cmd' in data:
            cls.answer(client, cls.json_answer({
                'errno': -2,
                'error': 'Use key: "cmd" for name of your command!'
            }))
            return None

        cmd = data['cmd']

        token = None
        if 'token' in data:
            token = data['token']


        if not cmd in cls.get_commands():
            answ = {
                 'errno': -3,
                 'error': 'Undefined command!'
            }
            if token is not None:
                answ['token'] = token
            cls.answer(client, cls.json_answer(answ))
            return None

        ## Executing command:
        cmd_ = cls.get_commands()[cmd]
        cmd_ = cls.configure_command(cmd_, client, data)
        answ = cmd_()
        if token is not None:
            answ['token'] = token
        cls.answer(client, cls.json_answer(answ))

        return 1

    ## Configure single command:
    @classmethod
    def configure_command(cls, command, client, data):
        return command(client, data)

    ## Send answer to client:
    @classmethod
    def answer(cls, client, data):
        ## Write data to client:
        client.write(data, client._on_write_complete)


class CommandsUDP(Commands):
    ## Send answer to client:
    @classmethod
    def answer(cls, client, data):
        ## Write data to client:
        client.write(data)

