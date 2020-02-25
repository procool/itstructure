import logging
import gevent
__import__('gevent.monkey').monkey.patch_all()


from client3 import Client

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

if __name__ == '__main__':
    c = Client(host='10.2.0.3', port=8102)
    c.start()
    print "Executing 10 requests:"
    for i in xrange(10):
        print c.echo()
    print "done"
    gevent.sleep(5)

    print "Executing 20 requests:"
    for i in xrange(20):
        print c.echo()
    print "done"
    gevent.sleep(10)

    print "Executing 10000 requests in 100 threads:"

    def echo_10(count=10):
        for i in xrange(count):
            print c.echo()

    gevent.joinall(
        [ gevent.spawn(echo_10, 100) for i in xrange(100) ],
        ## timeout=10,
    )
    print "done"
    
    gevent.sleep(10)
    print c.echo()
    print "Starting pinger..."

    while True:
        try:
            print c.echo()
        except Exception as err:
            print "Error on executing command!", err
        gevent.sleep(1)


