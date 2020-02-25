import sys, os, time, atexit
from signal import SIGTERM
 
class BaseDaemon(object):
    """
    A generic daemon class.
       
    Usage: subclass the Daemon class and override the run() method
    """

    logfile = None
    stdin   = "/dev/null"
    stdout  = "/dev/null"
    stderr  = "/dev/null"
    chdir   = None
    pidfile = None
    pid_rm_on_stop = True ## Remove pid file on stop

        
    def __init__(self, pidfile=None, stdin=None, stdout=None, stderr=None, chdir=None, ):
        self.stdin   = stdin or self.stdin
        self.stdout  = stdout or self.stdout
        self.stderr  = stderr or self.stderr
        self.pidfile = pidfile or self.pidfile
        self.chdir   = chdir or self.chdir
       
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
        # decouple from parent environment
        if self.chdir is not None: os.chdir(self.chdir)
        os.setsid()
        os.umask(0)
       
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)
       
            if self.logfile is not None:
                self.stdout = self.logfile
                self.stderr = self.logfile

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = isinstance(self.stdout, file) and self.stdout or file(self.stdout, 'a+')
        se = isinstance(self.stderr, file) and self.stderr or file(self.stderr, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
       
        # write pidfile
        atexit.register(self.delpid)
        self.pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % self.pid)
       
    def delpid(self):
        if not self.pid_rm_on_stop:
            file(self.pidfile,'w+').write("")
            return None
        os.remove(self.pidfile)
 
    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        ##except IOError:
        except Exception as err:
            pid = None
       
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
           
        # Start the daemon
        self.daemonize()
        self.run()
 
    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        ##except IOError:
        except Exception as err:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart
 
        sys.stdout.flush()
        sys.stderr.flush()

        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile) and self.pid_rm_on_stop:
                                        self.delpid()
            else:
                print str(err)
                sys.exit(1)
 
    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()
 
    def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
