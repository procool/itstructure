import logging

import os, sys
import traceback


class Command(object):

    def __init__(self, client, request):
        self.client  = client
        self.request = request

    def make_response(self, errno=0, error="OK", details = '', **kwargs):
        answer = {
            'errno' : errno,
            'error' : error,
            'details' : details,
        }
        answer.update(kwargs)
        return answer

    def make_answer(self, errno=0, error="Ok", details="", **kwargs):
        return self.make_response(errno, error, details, **kwargs)

    def make_error(self, errno=-1, error="Faild", details="", **kwargs):
        return self.make_response(errno, error, details, **kwargs)
 
    def process(self):
        try: 
            return self.make_answer(**self.request)
        except TypeError as err:
            return self.make_error(-5, 'Parametrs error!', details=str(err))
        except Exception as err:
            logging.error("Command error: %s" % err)
            data = traceback.format_exception(*sys.exc_info())
            for s in data:
                logging.error(s)
            logging.error('===================')

            return self.make_error(-4, 'Internal server error!', details=str(err))

    def __call__(self):
        return self.process()

