import logging
import re
import md5
import datetime
import json

from flask import abort
from flaskcbv.response import Response
from flaskcbv.view.mixins import JSONMixin
from flaskcbv.conf import settings

from misc.mixins_local import DefaultContextVars as DefaultContextVarsBase


class DefaultContextVars(DefaultContextVarsBase):
    __re_token = re.compile(r'^[a-zA-Z0-9]+$')

    def get_context_data(self, *args, **kwargs):

        context_ = {}
        try:
            token=self.request.args['_token'][0:20]
            if len(token) > 20 or not self.__re_token.match(token):
                raise Exception("wrong token")
            context_['_TOKEN'] = token
        except:
            context_['_TOKEN'] = None
        context = super(DefaultContextVars, self).get_context_data(*args, **kwargs)
        context_.update(context)
        return context_






class HelperMixin(object):
    def __init__(self, *args, **kwargs):
        self.is_helper = False
        return super(HelperMixin, self).__init__(*args, **kwargs)

    def helper_response(self):
        return Response(self.helper())

    @staticmethod
    def description():
        return u''

    def check_is_helper(self, *args, **kwargs):
        if hasattr(self, 'helper'):
            try: helper=self.request.args['helper'][0].lower()
            except: helper='no'
            if helper in ('y', 't', '1', 1,):
                self.is_helper = True
                return self.helper_response()
            self.is_helper = False
            raise Exception('not_a_helper')

    def dispatch(self, request, *args, **kwargs):
        try: return self.check_is_helper(*args, **kwargs)
        except: pass
        return super(HelperMixin, self).dispatch(request, *args, **kwargs)







class AuthMixin(object):
    def dispatch(self, *args, **kwargs):
        if self.request.user_id < 0:
            self.abort_error(errno=-1, error="wrong_session", details="session is not correct or expired")
        return super(AuthMixin, self).dispatch(*args, **kwargs)

    def prepare(self, *args, **kwargs):
        try: 
            session = self.get_argument_smart('session')
            r_ = settings._BB_CLIENT.session(session, self.current_url)
            if r_.errno < 0:
                self.request.user_id = -1
            else:
                self.request.user_id = r_.uid
                self.request.user_success = True
                self.request.user_session = r_.session
                self.request.user_access = r_.access
        except Exception as err:
            self.request.user_id = 0
            self.request.user_access = []
        return super(AuthMixin, self).prepare(*args, **kwargs)

