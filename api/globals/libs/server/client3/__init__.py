""" This client2 supports multiply async requests """

import sys, traceback

import random
import string

import logging
import time
import gevent
import json

from connector import Connector

LOGGING_PREFIX = "TCP CLIENT3: "
DEBUG=False

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
#logger.setLevel(logging.DEBUG)


class AttributeInitType(type):
    def __call__(self, *args, **kwargs):
        obj = type.__call__(self, *args)
        for name in kwargs:
            setattr(obj, name, kwargs[name])
        setattr(obj, 'as_dict', kwargs)
        return obj


class CommandResult(object):
    __metaclass__ = AttributeInitType

def result_wrapper(func):
    def wrapped(*args, **kwargs):
        r = func(*args, **kwargs)
        if r is not None:
            r = CommandResult(**r)
        return r
    return wrapped
    
def test_for_result(func):
    def wrapped(*args, **kwargs):
        r = func(*args, **kwargs)
        if r is None:
            raise(Exception("No Answer!"))
        elif not hasattr(r, 'errno'):
            raise(Exception("Proto error!"))
        return r
    return wrapped



class Command(object):
    timeout_default = 7
    max_trys = 1
    
    def __init__(self, name, data, timeout=None):
        self.crdate = time.time()
        if timeout is not None:
            self.timeout = timeout
        else:
            self.timeout = self.timeout_default
        self.connector = None
        self.wait_until = None
        self.trys = 0
        self.status = 0 # 0: new, 1: sending, 2: sent, 3: recv, 4: error
        self.result = None
        self.name = name
        self.data = data
        self.token = self.gen_token()

    def gen_token(self):
        return "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))

    def get_data(self):
        data = self.data or {}
        data.update({
            'cmd' : self.name,
            'token': self.token,
        })
        return data

    @property
    def is_complete(self):
        return self.status > 2 and True or False

    @property
    def is_error(self):
        return self.status > 3 and True or False

    def set_sent(self, status=2):
        self.status = status
        self.wait_until = self.crdate + self.timeout


    def set_complete(self, status=3):
        self.status = status

    def set_error(self, status=4):
        self.set_complete(status)

    @property
    def has_trys(self):
        return self.trys < self.max_trys and True or False

    def run_once(self):
        if self.status == 3:
            return self.result

        if self.wait_until is not None and time.time() > self.wait_until:
            self.set_error()
            logger.error(LOGGING_PREFIX + '%s:%s Command %s(%s) terminated by timeout(%s sec): %s' % (self.connector.host, self.connector.port, self.name, self.token, self.timeout, self.get_data()))

        if self.is_error:
            raise(Exception("Get command answer faild!"))

        return None


               
            

class Client(object):

    def __init__(self, host, port, ping_it=True, incoming=None, timeout=None, **kwargs):

        self.last_ping_timeout = time.time()
        self.timeout = timeout
        self.incoming = incoming
        self.cursor = Connector(host, port, on_connect=self.on_connect, run_once=self.run_once, **kwargs)
        self.is_exit = False
        self.ping_it = self.cursor.socket_timeout > 5 and ping_it or False
        self.has_commands = False
        self.__last_read = time.time()
        self.is_started = False

        self.buffer = {}
        self.lastupdate = time.time()
        self.cursor.connect()
        self.start()

    def commands_mark_failed(self):
        for token in self.buffer:
            self.buffer[token].set_error()

    def on_connect(self):
        self.commands_mark_failed()

    @property
    def address(self):
        return [self.cursor.host, self.cursor.port]

    @property
    def is_connected(self):
        return not self.cursor.is_dead and True or False

    @property
    def ready_to_ping(self):
        if not self.ping_it:
            return False

        if not self.is_connected:
            return False

        if self.last_ping_timeout+5 >= time.time():
            return False

        ping_time = self.lastupdate + self.cursor.socket_timeout - 5
        if time.time() <= ping_time:
            return False

        return True

    def echo(self, **kwargs):
        '''Push echo command to server.

        @return: True on success.
        @rtype: boolean
        '''
        res = self.exec_command('echo', test_data=123, **kwargs)
            
        if res is not None and \
           hasattr(res, 'cmd') and res.cmd == 'echo' and \
           hasattr(res, 'test_data') and res.test_data == 123:
            return True
        return False


    def ping(self, **kwargs):
        '''Push ping command to server.

        @return: True on success.
        @rtype: boolean
        '''
        res = self.exec_command('ping', **kwargs)
        if res is not None and hasattr(res, 'cmd') and res.cmd == 'pong':
            return True
        return False

        
        
            
    @test_for_result
    def quit(self, **kwargs):
        return self.exec_command('quit', **kwargs)
        
            
                

    ## Test Client for not processed(status==1) commands:
    def test_has_commands(self):
        for token in self.buffer:
            if self.buffer[token].status == 1:
                self.has_commands = True
                return True
        self.has_commands = False
        return False






    @result_wrapper
    def exec_command(self, cmd, **to_send):

        try: timeout = to_send.pop('timeout')
        except Exception as err: timeout = self.timeout

        command = Command(cmd, to_send, timeout=timeout)
        command.connector = self.cursor
        if DEBUG:
            logger.debug(LOGGING_PREFIX + "Sending command: %s" % json.dumps(command.get_data()))

        self.buffer[command.token] = command

        err_ = None
        while command.has_trys:
            try: 
                r = self.__exec_command(command)
                del self.buffer[command.token]
                self.test_has_commands()
                return r
            except Exception as err:
                err_ = err
            if command.has_trys:
                gevent.sleep(1) ## sleep after every fail
        self.test_has_commands()
        del self.buffer[command.token]
        raise(err_)


    
    def __exec_command(self, command):

        if not self.is_connected:
            command.trys += 1
            raise(Exception("No connection!"))
        
        ## Sending command:
        self.__send_command(command)
        if command.is_error:
            raise(Exception("Error on command send!"))

        ## Getting answer:
        while True:
            try: 
                r = command.run_once()
            except Exception as err:
                raise(err)

            if r is not None or command.is_complete:
                return command.result

            gevent.sleep(0.001)
        


    def __send_command(self, command):
        command.status = 0
        command.trys += 1
        try:
            self.cursor.send_cmd(command)
            self.has_commands = True
            return True
        except Exception as msg:
            self.__socket_error('connection closed on send: %s' % msg)
            if not command.has_trys:
                command.set_error()
            return False



    def __socket_error(self, comment=''):
        self.cursor.mark_dead(comment)
        if not self.cursor.do_reconnect:
                self.stop()





    def close(self):
        self.stop()

    def stop(self):
        self.is_exit = True
        logger.info(LOGGING_PREFIX + "Client stoped: %s:%s" % (self.cursor.host, self.cursor.port))
        self.cursor.stop()
        self.commands_mark_failed()

    def start(self):
        if self.is_started:
            return False
        self.is_started = True
        gevent.spawn(self.cursor.run)


    def run_once(self):
        if self.is_exit:
            self.cursor.stop()

        for answ in self.cursor.readlines():
            try: self.process_answer(answ)
            except Exception as err:
                pass

        ## No data to read, but waiting answer.. closing connection by self.cursor.socket_timeout:
        ##  ext_ = self.__last_read + self.cursor.socket_timeout
        ##    if ext_ < time.time():
        ##        self.__socket_error('connection closed in readline() by timeout: %s' % self.cursor.socket_timeout)

        def ping():
            self.last_ping_timeout = time.time()
            try: r = self.ping()
            except Exception as err: 
                r = False
                ##logging.error("Echo error: %s" % err)
            logger.info(LOGGING_PREFIX + "PING Server %s:%s: %s" % (self.cursor.host, self.cursor.port, r))

        ## Ping server by timeout:
        if self.ready_to_ping:
            gevent.spawn(ping)
                
        gevent.sleep(0.00001)


    @property
    def update_timeout(self):
        return time.time() - self.lastupdate
        



    def process_answer(self, answer):

        self.__last_read = time.time()

        if DEBUG:
            logger.debug(LOGGING_PREFIX + "Recv answer: %s" % repr(answer))

        try:
            r = json.loads(answer)
        except Exception as err:
            logger.error(LOGGING_PREFIX + 'Wrong answer type: JSON error: %s, DATA: """%s"""' % (err, repr(answer)))
            raise(err)

        if not 'token' in r:
            return None

        if r['token'] == 'INC' and self.incoming is not None:
            self.lastupdate = time.time()
            try:
                self.incoming(r)
            except Exception as err:
                logger.error(LOGGING_PREFIX + "CLIENT: INCOMING EXCEPTION: %s" % err)
                logger.error(LOGGING_PREFIX + "CLIENT: INCOMING: %s" % dir(self.incoming))
                data = traceback.format_exception(*sys.exc_info())
                for s in data:
                    logger.error(s)
                logger.error('===================')


        ## Undefined answer:
        if not r['token'] in self.buffer:
            return None

        self.buffer[r['token']].result = r
        self.buffer[r['token']].set_complete()
        self.lastupdate = time.time()

        return r

