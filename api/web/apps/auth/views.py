from flask import url_for
from flaskcbv.view import View
from flaskcbv.conf import settings

from misc.mixins import HelperMixin
from misc.views import JSONView



class authView(JSONView):

    def helper(self):
        return """Authorizaion handler
        Use "login" and "passwd" arguments by GET or POST to get session 
        """
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            username = self.get_argument_smart('username')
            passwd = self.get_argument_smart('password')
        except Exception as err:
            self.abort_error(errno=-1, error="wrong_params", details="set arguments: 'username', 'passwd'")
            
        r = settings._BB_CLIENT.login(username, passwd)
        answ = r.as_dict
        del answ["cmd"]
        del answ["token"]
        self.abort_error(**answ)
        



class sessionView(JSONView):

    def helper(self):
        return """Session check handler
        Use "session" argument by GET or POST to check your session
        """
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        try:
            session = self.get_argument_smart('session')
        except Exception as err:
            self.abort_error(errno=-1, error="wrong_params", details="set argument: 'session'")

        r = settings._BB_CLIENT.session(session)
        answ = r.as_dict
        del answ["cmd"]
        del answ["token"]
        self.abort_error(**answ)




