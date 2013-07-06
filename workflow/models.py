# -*- coding: utf-8 -*-

from django.db import models
from fields import WorkflowField
import json

class Workflow(models.Model):
    name = models.CharField(max_length=256, unique=True)
    workflow = WorkflowField()

    # def __init__(self, name, workflow=None, *args, **kwargs):
    #     super(Workflow, self).__init__(name, *args, **kwargs)
    #     if workflow is None:
    #         self.workflow = WF(name, **kwargs)
    #     elif isintance(workflow, WF):
    #         self.workflow = workflow

    # @property
    # def workflow(self):
    #     return WF.parse(json.loads(self._workflow))

    # @workflow.setter
    # def workflow(self, wf):
    #     self._workflow = json.dumps(wf.__dict__())

    # def save(self, *args, **kwargs):
    #     super(Workflow, self).save(*args, **kwargs)
