import time, datetime
import math
import pytz
from flaskcbv.view.mixins import getArgumentMixin

from libs.db import get_db_session
from formview import CRUDFormMixin


DBECHO = True

dbsession = get_db_session(echo=DBECHO)

class CRUDObjectsMixin(object):

    def __init__(self, *args, **kwargs):
        self._pk = None
        self._dbsession = dbsession
        super(CRUDObjectsMixin, self).__init__(*args, **kwargs)

    def get_model(self):
        return self.model

    def get_query_postfix(self, qs):
        return qs

    def get_queryset(self):
        model = self.get_model()
        return self._dbsession.query(model)


    def get_json_default(self):
        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime)):
                o_ = o.astimezone(pytz.utc)
                return {
                    "unix": time.mktime(o_.utctimetuple()),
                    "date": o_.strftime("%d/%m/%y"),
                    "time": o_.strftime("%H:%M"),
                    "tuple": o_.utctimetuple(),
                }
        return default


    def get_json_kwargs(self, **kwargs):
        kwargs = super(CRUDObjectsMixin, self).get_json_kwargs()
        kwargs["default"] = self.get_json_default()
        return kwargs



    def get_object(self):
        if hasattr(self, '__instance'):
            return getattr(self, '__instance')

        if self._pk is None:
            return None
        obj = self.get_queryset()
        if self.is_batch:
            obj = obj.filter(self.get_model().id.in_(self._pk))
        else:
            obj = obj.filter(self.get_model().id==self._pk)

        if self.is_batch:
            setattr(self, '__instance', obj)
        else:
            setattr(self, '__instance', obj.first())
        return self.get_object()


    def prepare(self, *args, **kwargs):
        r = super(CRUDObjectsMixin, self).prepare(*args, **kwargs)
        self._dbsession.close()
        return r




class CRUDListMixin(getArgumentMixin, CRUDObjectsMixin):

    """
    redefine perpage and perpage_max
    Also, you should defined next attributes:
    model = YourModel
    list_fields = [] - list of available result fields
    """
    perpage = 10
    perpage_max = 1000

    list_fields = []


    def helper(self):
        try: r = super(CRUDListMixin, self).helper()
        except: r = ''
        r += """ Helper of list
        """
        return r


    def get_query_postfix(self, qs):
        try:
            qs = super(CRUDListMixin, self).get_query_postfix(qs)
        except: 
            pass

        if not hasattr(self, "pages_total") or self.pages_total is None:
            pages_total_ = math.ceil( float(qs.count())/float(self._perpage) )
            self.pages_total = int(pages_total_) or 1
        if self._page > self.pages_total:
            self._page = self.pages_total
        qs = qs.limit(self._perpage)
        page_ = self._page - 1
        if page_ < 0:
            page_ = 0
        self._page = page_+1
        offset_ = page_*self._perpage
        qs = qs.offset(offset_)
        return qs

    def get_list(self):
        qs = self.get_queryset()
        return self.get_query_postfix(qs)

    def get_context_data(self, **kwargs):
        context = super(CRUDListMixin, self).get_context_data(**kwargs)
        context["result"] = []
        for item in self.get_list().all():
            res = {}
            for fld in self.list_fields:
                if isinstance(fld, dict):
                    if "name" not in fld or "call" not in fld:
                        continue
                    res[fld["name"]] = fld["call"](item)
                    continue
                
                try:
                    res[fld] = getattr(item, fld)
                except Exception as err:
                    pass
            context["result"].append(res)
        context["page"] = self._page
        context["perpage"] = self._perpage
        return context


    def prepare(self, *args, **kwargs):
        try: self._page = int(self.get_argument_smart('page'))
        except: self._page = 1
        try: self._perpage = int(self.get_argument_smart('perpage'))
        except: self._perpage = self.perpage
        if self._perpage > self.perpage_max:
            self._perpage = self.perpage

        return super(CRUDListMixin, self).prepare(*args, **kwargs)



class CRUDDetailsMixin(getArgumentMixin, CRUDObjectsMixin):
        
    list_fields = []

    def helper(self):
        try: r = super(CRUDDetailsMixin, self).helper()
        except: r = ''
        r += """ Helper of list
        """
        return r

    def get_details(self):
        ## FIXME: GetObject!!!
        return self.get_queryset()



    def get_context_data(self, **kwargs):
        context = super(CRUDDetailsMixin, self).get_context_data(**kwargs)
        context["result"] = {}

        item = self.get_list().first()
        if item is None:
            self.abort_error(error='notexist', details='Object with given key does not exist!')

        for fld in self.list_fields:
            if isinstance(fld, dict):
                if "name" not in fld or "call" not in fld:
                    continue
                res[fld["name"]] = fld["call"](item)
                continue
            try:
                res[fld] = getattr(item, fld)
            except Exception as err:
                pass
        context.append(res)
        return context


    def dispatch(self, request, pk=None, **kwargs):
        try:
            self._pk = int(pk)
        except Exception as err:
            self.abort_error(error='pk', details='Object key error: %s' % err)
       

        try:
            return super(CRUDDetailsMixin, self).dispatch(request, **kwargs)
        except Exception as err:
            logger.error('FORMVIEW: REAL ERROR: %s' % err)
            data = traceback.format_exception(*sys.exc_info())
            return self.abort_error(error='failed', details='%s' % err, traceback=["%s" % s for s in data])







class CRUDUpdateMixin(getArgumentMixin, CRUDObjectsMixin, CRUDFormMixin):
    pass


