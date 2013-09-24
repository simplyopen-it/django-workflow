# -*- coding: utf-8 -*-
from django.db import models

class WorkflowManager(models.Manager):

    def get_node_superset(self, filter=None, exclude=None):
        if filter is None:
            filter = {}
        if exclude is None:
            exclude = {}
        workflows = self.filter(**filter).exclude(**exclude)
        ret = set()
        for wf in workflows:
            ret = ret.union(set([(node.name, node.label) for node in wf.itervalues()]))
        return ret
