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
        return WF.parse(json.loads(value))

    def get_prep_value(self, value):
        if not isinstance(value, WF):
            raise TypeError("value not a Graph instance")
        return json.dumps(value.__dict__)
