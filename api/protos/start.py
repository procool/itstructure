# -*- coding: utf-8 -*-

import os, sys
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')
##logging.basicConfig(level=logging.INFO, format='%(levelname)s - - %(asctime)s %(message)s', datefmt='[%d/%b/%Y %H:%M:%S]')

sys.path.append('@GLOBALS@')
sys.path.append('@WEB@')
sys.path.append('@APPS@')

os.environ.setdefault("FLASK_SETTINGS_MODULE", "settings")

from project import application

if __name__ == "__main__":
    host = "0.0.0.0"
    port = 7999
    print "\nStarting on: %s:%d" % (host, port)
    application.run(debug=True, host=host, port=port)

