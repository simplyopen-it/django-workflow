# -*- coding: utf-8 -*-
from django.db import models

class WorkflowManager(models.Manager): # pylint: disable=W0232

    def get_node_superset(self, filter_=None, exclude=None):
        if filter_ is None:
            filter_ = {}
        if exclude is None:
            exclude = {}
        return self.filter(**filter_).exclude(**exclude).values_list('node__name', 'node__label').distinct()
