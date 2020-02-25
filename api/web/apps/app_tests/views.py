import json
import logging
from flaskcbv.response import Response
from flaskcbv.view.mixins import JSONMixin
from flaskcbv.view import View
from flask import session

from misc.mixins import HelperMixin
# from auth.views import LoginRequiredMixin

class jsonView(JSONMixin, View):

    def get_context_data(self):
        context = super(jsonView, self).get_context_data()
        context['testvar'] = 'testval'
        return context


    def dispatch(self, request, *args, **kwargs):
        answ = self.get_as_json(details="you should see 'testvar' variable in this answer")

        return Response(answ)
        


class errorView(JSONMixin, View):
    def dispatch(self, request, *args, **kwargs):
        answ = self.json_error(error='test_error', details='If you see this error, then view is worked!:)')
        return Response(answ)


#class sessionView(JSONMixin, View):
#    def dispatch(self, request, *args, **kwargs):
#        session['test'] = '123'
#        answ = self.get_as_json(details="is there is a 'session' variable in cookie?!")
#        return Response(answ)


#class authedView(LoginRequiredMixin, JSONMixin, View):
#    def dispatch(self, request, *args, **kwargs):
#        answ = self.get_as_json(details="session is valid!")
#        return Response(answ)




