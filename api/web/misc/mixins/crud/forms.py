import json
import logging

from flaskcbv.forms import Form as FormBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FormMixin(object):
    ## Disable it by setting to None:
    as_json_attr = "jsondata"
    field_prefix = "fld-"
    fields = None

    def __init__(self, instance=None, data={}, view=None):
        self.instance = instance
        self.data = data
        self.view = view
        self.cleaned_data = {}
        self.errors = {}
        self._make_auto_fields()
        self.check_data_as_json()

    ## Replace data with json one:
    def check_data_as_json(self):
        if self.as_json_attr is not None and self.as_json_attr in self.data:
            try:
                self.data = {}
                data = json.loads(data[self.as_json_attr])
                for key, val in data.items():
                    self.data["%s%s" % (self.field_prefix, key)] = val
                    
            except Exception as err:
                self.error[self.as_json_attr] = "%s" % err


    def clean(self, *args, **kwargs):

        if self.view.is_delete:
            return None

        clean_defs = []
        if hasattr(self, 'get_clean_defs'):
            clean_defs = self.get_clean_defs()

        for attr in dir(self):
            if not attr.startswith('clean_'):
                continue
            if attr in clean_defs:
                continue
            clean_defs.append(attr)

        for attr in clean_defs:
            item = attr[6:]
            ident = "%s%s" % (self.field_prefix, item)
            value = None
            if ident in self.data:
                value = self.data[ident]
            try:
                value = getattr(self, attr)(value)
                if value is not None:
                    self.cleaned_data[item] = value
            except Exception as err:
                self.errors[item] = str(err)
                continue


    @property
    def is_clean(self):
        if len(self.errors.keys()) == 0:
            return True
        return False


    def submit(self, instance=None):
        if instance is None:
            instance = self.instance

        if instance is None:
            return None

        for attr in self.cleaned_data:
            try:
                setattr(instance, attr, self.cleaned_data[attr])
                try: logger.info('FORMS: SETTING ATTR: "%s": (%s) %s' % (attr, getattr(instance, attr), type(getattr(instance, attr))))
                except: logger.info('FORMS: SETTING ATTR: "%s": (%s) OK!' % (attr, type(getattr(instance, attr)) ))
            except Exception as err:
                try: logger.error('FORMS: SETTING ATTR ERROR: "%s": "%s": %s' % (attr, self.cleaned_data[attr], err))
                except: logger.error('FORMS: SETTING ATTR ERROR: "%s": %s' % (attr, err))

        instance = self.save(instance=instance)
        return instance

    def save(self, instance=None, **kwargs):
        if instance is None:
            instance = self.instance
        if instance is None:
            return None
        self.view._dbsession.add(instance)
        self.view._dbsession.commit()
        return instance




    def _make_auto_fields(self):
        if self.fields is None:
            return None

        avail_types = ("str", "int")
        def make_clean_def(**setts):
            req = ("required" in setts and setts["required"]) and True or False
            t = ("type" in setts and setts["type"] in avail_types) and setts["type"] or "str"
            def wrapped(val):
                if val is None and (not req or self.instance is not None):
                    return None
                elif val is None and self.instance is None:
                    raise Exception("required")

                if t == "str":
                    if "min" in setts and setts["min"] is not None:
                        if setts["min"] > 0 and len(val) < setts["min"]:
                            raise Exception("too_short:%d" % setts["min"])

                    if "max" in setts and setts["max"] is not None:
                        if setts["max"] > 0 and len(val) > setts["max"]:
                            raise Exception("too_long:%d" % setts["max"])
                       
                    if "limit" in setts and setts["limit"] is not None and setts["limit"] > 0:
                        return val[0:setts["limit"]]
                    return val

                elif t == "int":
                    return int(val)
            return wrapped

        for fld, fdata in self.fields.items():
            setattr(self, "clean_%s" % fld, make_clean_def(**fdata))
                
            


class Form(FormMixin, FormBase):
    pass

