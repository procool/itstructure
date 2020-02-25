import logging
import gevent
__import__('gevent.monkey').monkey.patch_all()


from client3 import Client

class BBClient(Client):
    proto_version="1.0"
    def on_connect(self):
        self.cursor.send("BBPROTO/%s\r\n\r\n" % self.proto_version)
        return super(BBClient, self).on_connect()

    def login(self, user, passwd, url=None, **kwargs):
        """Login user by username and password

        @return: settings with session on success, otherwise None
        @rtype: clientresponse object
        """
        setts = {
            "user": user, 
            "password": passwd, 
        }
        if url is not None:
            setts["url"] = url
        setts.update(kwargs)
        res = self.exec_command('login', **setts)
        return res


    def session(self, session, url=None, **kwargs):
        """Check Session

        @return: settings with session on success, otherwise None
        @rtype: clientresponse object
        """
        setts = {
            "session": session,
        }
        if url is not None:
            setts["url"] = url
        setts.update(kwargs)
        res = self.exec_command('session', **setts)
        return res



logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

if __name__ == '__main__':
    c = BBClient(host='127.0.0.1', port=8890)
    c.start()
    print "Executing 10 requests:"
    for i in xrange(10):
        print c.echo()
    print "done"
    gevent.sleep(5)


