# -*- coding: utf-8 -*-
from django.db import models
from graph import Graph as WF
import json


class WorkflowField(models.TextField):

    __metaclass__ = models.SubfieldBase

    description = 'A django workflow'

    def to_python(self, value):
        if value is None:
            return None
        if value == '':
            value = '{}'
        if isinstance(value, WF):
            return value
        if isinstance(value, (str, unicode)):
            return value.replace('null', 'None')
        return WF.parse(json.loads(value))

    def get_prep_value(self, value):
        if isinstance(value, WF):
            ret = json.dumps(value.__dict__)
        elif isinstance(value, (str, unicode)):
            ret = json.dumps(eval(value))
        else:
            raise ValueError("value not a Graph instance")
        return ret