# -*- coding: utf-8 -*-
from django.db import models
from workflow.graph import Graph as WF
import json


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
        # elif isinstance(value, (str, unicode)):
        #     value = value.replace('null', 'None')
        #     ret = json.dumps(eval(value))
        # else:
        #     raise ValueError("value not a Graph instance")
        else:
            ret = json.dumps(value)
        return ret
