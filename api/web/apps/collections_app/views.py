from flask import url_for
from flaskcbv.view import View
from misc.mixins import HelperMixin
from misc.mixins.crud import CRUDListMixin, CRUDDetailsMixin, CRUDUpdateMixin

from misc.views import JSONView

from models.collections.sa_models import Categories
from .forms import CategoriesForm


class categoriesListView(CRUDListMixin, JSONView):
    description = "List of collection categories"
    model = Categories
    list_fields = ["id", "ident", "name", "comment", "tags", "description", "crdate",]

    def get_queryset(self):
        qs = super(categoriesListView, self).get_queryset()
        if self.__parentid is not None:
            qs = qs.filter(Categories.parent_id==self.__parentid)
        return qs


    def dispatch(self, request, parentid=None, **kwargs):
        ## Get parent ID:
        try:
            self.__parentid = int(parentid)
        ## No parentid, show root of tree:
        except Exception as err:
            self.__parentid = None

        return super(categoriesListView, self).dispatch(request, **kwargs)



class categoriesUpdateView(CRUDUpdateMixin, JSONView):
    description = "Update category(ies)"
    model = Categories
    form_class = CategoriesForm




            



