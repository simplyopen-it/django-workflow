# -*- coding: utf-8 -*-
from django.db import models
from django_extensions.db.fields.json import JSONField
from workflow.graph import Graph as WF
import json


class JSONListUniqueField(JSONField):

    def pre_save(self, model_instance, add):
        value = super(JSONListUniqueField, self).pre_save(model_instance, add)
        # make values unique
        if value is not None:
            value = list(set(value))
            setattr(model_instance, self.attname, value)
        return value


class WorkflowField(models.TextField):

    __metaclass__ = models.SubfieldBase

    description = 'A django workflow'

    def to_python(self, value):
        ''' DB value to Python '''
        if value is None:
            return None
        if value == '':
            value = '{}'
        if isinstance(value, WF):
            return value
        if isinstance(value, (str, unicode)):
            try:
                # This happens when saving a Form value
                value = json.loads(value.replace('None', 'null'))
            except ValueError:
                # This happends when loading a Form value
                return value.replace('null', 'None')
        return WF.parse(value)

    def get_prep_value(self, value):
        ''' Python to DB value '''
        if isinstance(value, WF):
            ret = json.dumps(value.__dict__)
        else:
            ret = json.dumps(value)
        return ret

    def south_field_triple(self):
        ''' Returns a suitable description of this field for South. '''
        # This method is not needed anymore after Django-1.6,
        # in its place there is deconstruct().
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        kwargs.pop('path', None)
        return ("workflow.fields.WorkflowField", args, kwargs)
