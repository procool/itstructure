import logging
import json
import md5

from flaskcbv.view.mixins import getArgumentMixin
from misc.mixins_local.crud.filters import ListFiltersBaseMixin

class ListFiltersMixin(ListFiltersBaseMixin, getArgumentMixin):

    def helper(self):
        try: r = super(ListFiltersMixin, self).helper()
        except: r = ''
        r += """
List Filters:
=============
    You can filter list by filters settings;

Avalible query arguments:
    filters - list of filtered fields in JSON format;

Avalible filters: 
    %(filters)s
    
        """ % { 
            'filters': self.get_sorted_filters(),
        }

        return r

    def get_context_data(self, **kwargs):
        context = super(ListFiltersMixin, self).get_context_data(**kwargs)
        try:
            context['avalible_filters'] = self.get_sorted_filters()
            context['avalible_filters_md5'] = md5.new("%s" % context['avalible_filters']).hexdigest()
        except Exception as err:
            logging.error("ListFiltersMixin: can't set get_context_data: %s" % err)
        return context


    def dispatch(self, request, *args, **kwargs):
        try: 
            filters_ = self.get_argument_smart('filters')
            ##logging.debug('FILTERS QS: %s' % filters_)
            ##print "EER", filters_
            self._qs_filters = json.loads(filters_)
        except Exception as err: 
            ##print "OOOups: %s" % err
            self._qs_filters = {}
        return super(ListFiltersMixin, self).dispatch(request, *args, **kwargs)







