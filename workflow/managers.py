# -*- coding: utf-8 -*-
from django.db import models


class WorkflowManager(models.Manager): # pylint: disable=W0232

    def get_by_natural_key(self, name):
        return self.get(name=name)

    def get_node_superset(self, filter_=None, exclude=None):
        if filter_ is None:
            filter_ = {}
        if exclude is None:
            exclude = {}
        return self.filter(**filter_).exclude(**exclude).values_list('node__name', 'node__label').distinct()


class WorkflowNodeManager(models.Manager):

    def get_by_natural_key(self, wf_name, node_name):
        return self.get(workflow__name=wf_name, name=node_name)
