import time, datetime

from misc.tzinfo import myTimeZone

class DefaultContextVars(object):
    def get_context_data(self, *args, **kwargs):
        context_ = {}

        dt_local = datetime.datetime.now(tz=myTimeZone(0))
        context_['DATETIME_UTC'] = dt_local.strftime('%Y/%m/%d %H:%M')
        context_['TIME_UTC'] = time.time()
        context = super(DefaultContextVars, self).get_context_data(*args, **kwargs)
        context_.update(context)
        return context_




