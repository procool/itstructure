import logging
import md5
from sqlalchemy import desc
from flaskcbv.view.mixins import getArgumentMixin
from misc.mixins_local.crud.filters.base import SAJoinsMixin

from misc.mixins_local.crud.sortmixin import SortViewBaseMixin

        
class SortViewMixin(SortViewBaseMixin, getArgumentMixin):

    def get_sort_fields(self):
        ##logging.info('SORT FIELDS0: %s' % self.__sort_fields)
        return self.__sort_fields


    def dispatch(self, request, *args, **kwargs):
        try:
            self.__sort_fields = self.get_argument_smart('sort_fields').split(',')
        except:
            self.__sort_fields = self.__get_sortsetts_by_session()

        return super(SortViewMixin, self).dispatch(request, *args, **kwargs)


    def __get_sortsetts_by_session(self):
        setts = self.get_list_setts()
        try: return setts['sort_fields']
        except: return None
        

    def get_context_data(self, **kwargs):
        context = super(SortViewMixin, self).get_context_data(**kwargs)

        try:
            fields_ = self.get_model_ordered_fields()
        except AttributeError:
            fields_ = []

        try:
            context['avalible_sort_fields'] = [ i_[0] for i_ in self.get_sort_fields_names(fields_)]
            context['avalible_sort_fields_md5'] = md5.new("%s" % context['avalible_sort_fields']).hexdigest()
        except Exception as err:
            logging.error("SortViewMixin: can't set get_context_data: %s" % err)
        return context



    def helper(self):

        try:
            fields_ = self.get_model_ordered_fields()
        except AttributeError:
            fields_ = []

        avalible_fields = '\n    '.join([ i_[0] for i_ in self.get_sort_fields_names(fields_)])


        try: r = super(SortViewMixin, self).helper()
        except: r = ''
        r += """
Sorting Helper:
===============
You can sort results ASC(up) or DESC(down) by selected fields;

Avalible query arguments:
    sort_fields: Comma separated list of sorting fields

If sort_fields is not defined, list will be sorted by defaults of model;

By default sort direction is down(ASC);
If field starts with '-', sort direction is up(DESC), e.g.:
   sort_fields=-SomeModel.id,crdate,-date_begin

Avalible fields for sorting: %(avalible_fields)s

        """ % { 'avalible_fields': avalible_fields, }

        return r


    """
    ## You should define it in your view
    ## Returns list of sortable fields

    def get_model_ordered_fields(self):
        ##return self.get_model()
        return []
    """






