from misc.mixins.crud.forms import Form

class CategoriesForm(Form):

    fields = {
        "ident": {"type":"str", "min": 2, "limit": 50, "required": True,},
        "name": {"type":"str", "min": 3, "limit": 250, "required": True,},
        "comment": {"type":"str", "limit": 250},
        "tags": {"type":"str", "limit": 250},
        "description": {"type":"str"},
        "parent_id": {"type":"int"},
    }


    """
    def clean_ident(self, val):
        return val[0:50]

    def clean_name(self, val):
        return val[0:250]

    def clean_comment(self, val):
        return val[0:250]

    def clean_tags(self, val):
        return val[0:250]

    def clean_description(self, val):
        return val

    def clean_parent_id(self, val):
        if val is not None:
            return int(val)

    """


