# -*- coding: utf-8 -*-
from django_extensions.db.fields.json import JSONField


class JSONListUniqueField(JSONField):

    def pre_save(self, model_instance, add):
        value = super(JSONListUniqueField, self).pre_save(model_instance, add)
        # make values unique
        if value is not None:
            value = list(set(value))
            setattr(model_instance, self.attname, value)
        return value
