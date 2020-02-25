import logging
import sys, traceback

from flaskcbv.response import Response, ResponseRedirect
from flaskcbv.view.crud import FormViewMixin

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CRUDFormMixin(FormViewMixin):
    csrf_check=False
    disable_on_delete=False
    only_post = False

    def __init__(self, delete=False, batch=False, **kwargs):
        self.is_delete = delete
        self.is_batch = batch
        super(CRUDFormMixin, self).__init__(**kwargs)

    ## FlaskCBV method:
    def get_form_class_kwargs(self, **kwargs):
        params = super(CRUDFormMixin, self).get_form_class_kwargs(**kwargs)
        try:
            params['instance'] = self.get_object()
        except Exception as err:
            params['instance'] = None
        return params

    def get(self, *args, **kwargs):
        if self.only_post:
            self.abort_error(error='failed', details='Use POST')
        self.request.form = self.request.args
        return self.post(*args, **kwargs)


    def post(self, request, pk=None, **kwargs):
        try:
            if self.is_batch:
                self._pk = map(int, [ i for i in pk.split(',') if i != ''])
            elif pk is not None:
                self._pk = int(pk)
        except Exception as err:
            self.abort_error(error='pk', details='Object key error: %s' % err)
        return super(CRUDFormMixin, self).post(request, **kwargs)



    def form_invalid(self, form, *args, **kwargs):
        self.abort_error(error='form_errors', details="Check your form data!", errors=form.errors)



    def form_valid(self, form, **kwargs):
        self.real_ip = self.request.remote_addr
        if 'HTTP_X_FORWARDED_FOR' in self.request.environ:
            self.real_ip = self.request.environ['HTTP_X_FORWARDED_FOR']

        ## On Object remove:
        if self.is_delete:
            obj = self.get_object()
            if obj is None:
                self.abort_error(error='notexist', details='Object with given key does not exist!')
            if self.is_batch:
                answ = []
                for item in obj:
                    answ.append(self.delete_object(item, form, **kwargs))
                self.abort_error(error='Ok', errno=0, batch=answ)
            else:
                answ = self.delete_object(obj, form, **kwargs)
                self.abort_error(**answ)

        if self.is_batch:
            answ = []
            obj = self.get_object()
            for item in obj:
                answ.append(self.__process_valid_form(form, instance=item, **kwargs))
            self.abort_error(error='Ok', errno=0, batch=answ)
        else:
            answ = self.__process_valid_form(form, **kwargs)
            self.abort_error(**answ)



    def __process_valid_form(self, form, **kwargs):
        logger.debug("FORMVIEW: FOR CRUD: DEBUG DATA: %s" % form.cleaned_data)
        try:
            return self.process_valid_form(form, **kwargs)
        except Exception as err:
            logger.error('FORMVIEW: REAL ERROR: %s' % err)
            data = traceback.format_exception(*sys.exc_info())
            for s in data:
                logger.error(s)
            logger.error('===================')
            return self.crud_error_data(details='%s' % err)




    def crud_error_data(self, **kwargs):
        answ = {'errno': 1, 'error': 'failed', 'details': ''}
        answ.update(kwargs)
        return answ



    def get_create_object(self):
        obj = self.get_object()
        is_new = False

        ## New item:
        if obj is None and self._pk is None:
            obj, is_new = self.get_model()(), True
        #elif self._pk is None:
        #    obj = self.get_model()()
        return [obj, is_new]


    def delete_object(self, obj, form, disable_it=False, **kwargs):
        id = obj.id
        if disable_it or self.disable_on_delete:
            if not hasattr(obj, 'disabled'):
                return self.crud_error_data(error='nodisabled', details='Object has no "disabled" attribute')
            obj.disabled = True
            self._dbsession.add(obj)
            self._dbsession.commit()
        else:
            self._dbsession.delete(obj)
            self._dbsession.commit()
        return self.crud_error_data(errno=0, error='Ok', id=id)


    def process_valid_form(self, form, instance=None, **kwargs):
        obj, is_new = self.get_create_object()
        if instance is not None:
            obj, is_new = instance, False
        if obj is None:
            return self.crud_error_data(error='notexist', details='Object with given key does not exist!')
        form.submit(instance=obj)
        return self.crud_error_data(errno=0, error='Ok', id=obj.id)







