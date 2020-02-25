import json
from flaskcbv.view import View
from flaskcbv.response import Response
from flaskcbv.view.mixins import getArgumentMixin

from misc.mixins import DefaultContextVars, HelperMixin, JSONMixin, AuthMixin


class AbortEx(Exception):
    def __init__(self, data, *args, **kwargs):
        self.errdata = data
        super(AbortEx, self).__init__("error", *args, **kwargs)



class JSONView(AuthMixin, DefaultContextVars, HelperMixin, getArgumentMixin, JSONMixin, View):

    def helper(self):
        try: r = super(JSONView, self).helper()
        except: r = ''
        r += """
JSON Helper:
============

If you use output=json, response will be given in unreadeble short format;
To get readeble format you can use `json_indent' GET argument(int, indent size)

Avalible query arguments:
    json_indent: int, indent size;

        """

        return r

    def abort_error(self, **kwargs):
        answ = {'errno': -1, 'error': 'failed', 'details': ''}
        answ.update(kwargs)
        raise AbortEx(answ)
        
    

    def get_json_indent(self):
        return self.__json_indent

    def dispatch(self, request, *args, **kwargs):
        try: self.__json_indent = int(request.args['json_indent'])
        except: self.__json_indent = None

        try:
            r = super(JSONView, self).dispatch(request, *args, **kwargs)
            if self.is_helper:
                return r
            return Response(self.get_as_json())
        except AbortEx as err:
            return Response(json.dumps(err.errdata, indent=self.get_json_indent()))

