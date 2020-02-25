import logging
import time
import socket, select
import json

LOGGING_PREFIX = "TCP CONNECTOR: "
DEAD_RETRY = 0.5       ## Retry time in seconds
SOCKET_TIMEOUT = 15
DEBUG=True

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class Connector(object):

    def __init__(self, host, port, dead_retry=DEAD_RETRY, 
                 socket_timeout=SOCKET_TIMEOUT, proto=None, 
                 max_rate=100, on_connect=None, do_reconnect=False, run_once=None):

        self.is_exit = False
        self.is_running = False

        self.host = host
        self.port = port
        self.dead_retry = dead_retry
        self.socket_timeout = socket_timeout
        self.on_connect = on_connect
        self.do_reconnect = do_reconnect
        self.run_once_callback = run_once
        self.family = socket.AF_INET
        self.max_rate = max_rate

        if proto == 'inet6':
            self.family = socket.AF_INET6

        self.address = ( self.host, self.port )

        self.deaduntil = 0
        self.__socket = None

        self.buffer_read = ''
        self.buffer_write = ''
        self.commands_to_send = {}


    @property
    def is_connected(self):
        if self.is_dead:
            return False
        if self.socket is None:
            return False
        return True 


    def mark_dead(self, reason):
        if self.is_dead:
            return True
        logger.info(LOGGING_PREFIX + "%s:%s: %s.  Marking dead." % (self.host, self.port, reason))
        if self.do_reconnect:
            self.deaduntil = time.time() + self.dead_retry
        else:
            self.deaduntil = -1
        self.close()


    @property
    def is_dead(self):
        if self.deaduntil > 0 and self.deaduntil > time.time():
            return True
        if self.deaduntil < 0:
            return True
        return False


    def connect(self):
        return self.socket
        

    @property
    def socket(self):
        if self.is_dead:
            return None
        if self.__socket is not None:
            return self.__socket

        ## Connect to server:
        if DEBUG:
            logger.debug(LOGGING_PREFIX + "Making connection to: %s:%s" % (self.host, self.port))
        s = socket.socket(self.family, socket.SOCK_STREAM)
        if hasattr(s, 'settimeout'): s.settimeout(self.socket_timeout)
        try:
            s.connect(self.address)
        except socket.timeout, msg:
            self.mark_dead("connect: %s" % msg)
            return None
        except socket.error, msg:
            if isinstance(msg, tuple): 
                msg = msg[1]
            self.mark_dead("connect: %s" % msg[1])
            return None
        ##s.setblocking(False)
        s.setblocking(0)
        self.__socket = s
        ##self.__socket.setblocking(False)
        self.buffer = ''
        if self.on_connect is not None:
            self.on_connect()
        return s


            
    def disconnect(self):
        self.close()

    def close(self):
        if self.__socket is None:
            return None
        if DEBUG:
            logger.debug(LOGGING_PREFIX + "Closing socket: %s" % self.__socket)
        self.__socket.close()
        self.__socket = None
        return True



    def readlines(self):

        while True:
            idx = self.buffer_read.find('\r\n')
            if idx < 0:
                break
            l = self.buffer_read[0:idx]
            self.buffer_read = self.buffer_read[idx+2:]
            yield l


    def send_cmd(self, command):
        raw_data = json.dumps(command.get_data())
        s, e, l = self.send(raw_data+'\r\n')
        self.commands_to_send[command.token] = [
            command,
            s, e, l,
        ]
        command.status = 1 ## Sending
        return True


    def send(self, data):
        """ data already has trailing \r\n's applied """
        sbyte = len(self.buffer_write)
        len_ = len(data)
        ebyte = sbyte+len_
        self.buffer_write += data
        return sbyte, ebyte, len_


    def stop(self):
        self.is_exit = True

    def run(self):
        bufftime = time.time()

        #iterations per second, max, mid:
        mid_rate = 0
        sleep_time = 0

        counter = 0
        self.is_running = True
        while True:
            if self.is_exit:
                break

            ## Run iteration callback:
            if self.run_once_callback is not None:
                self.run_once_callback()

            ## Run loop iteration, read from, write to socket:
            ## Connection is OK:
            if self.run_once():
                counter += 1
                ntime = time.time()
                if int(ntime) > bufftime:
                    bufftime = int(ntime)
                    mid_rate = counter
                    counter = 0
                    sleep_time = sleep_time + 1.0/self.max_rate - 1.0/mid_rate

            ## Connection error:
            else:
                sleep_time, mid_rate, counter = 1.0/self.max_rate, 0, 0

            ##print "SLEEP: %s, %s, %s" % (sleep_time, mid_rate, counter)
            if sleep_time > 0:
                time.sleep(sleep_time)

            ## Nothing to send, sleep:
            ##if sleep_time > 0 and len(self.buffer_write) == 0:
            ##    time.sleep(sleep_time)

        self.is_running = False

        self.close()


    def run_once(self):
        if not self.is_connected:
            return False

        fr, fw, fe = select.select([self.socket,], [self.socket,] , [])

        logger.debug("SELECT: %s %s" % (fr, fw))

        ## Can read:
        for fd in fr:
            if fd == self.socket:
                buffer = ''
                while True:
                    try: buff = self.socket.recv(4096)
                    except Exception as err: 
                        break
                    if len(buff) <= 0:
                        break
                    buffer += buff
                if len(buffer) == 0:
                    self.mark_dead('read_error')
                self.buffer_read += buffer

        ## Can write:
        for fd in fw:

            count = 0 ## writed bytes

            ## Write buffer to server:
            if fd == self.socket and len(self.buffer_write) > 0:
                try: 
                    count = self.socket.send(self.buffer_write)
                except Exception as err:
                    count = 0
                if count <= 0:
                    self.mark_dead('write_error')
                elif count < len(self.buffer_write):
                    self.buffer_write = self.buffer_write[count:]
                else:
                    self.buffer_write = ''


            ## Test for sent commands:
            to_remove = []
            for cmdtoken, dt in self.commands_to_send.items():
                command, s, e, l = dt
                if e <= count:
                    command.set_sent() ## Sent


                elif e > count:
                    self.commands_to_send[cmdtoken][1] = s - count
                    self.commands_to_send[cmdtoken][2] = e - count

                ## Allready sent or error:
                if command.status > 1:
                    to_remove.append(cmdtoken)

            ## Removing sent commands:
            for cmdtoken in to_remove:
                if cmdtoken in self.commands_to_send:
                    del self.commands_to_send[cmdtoken]

        return True



