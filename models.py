# -*- coding: utf-8 -*-

from django.db import models
from workflow import Workflow
import json

class Workflow(models.Mode):
    _workflow = model.TextField()

    @property
    def workflow(self):
        return Workflow.parse(json.loads(self._workflow, null=True))

    @workflow.setter
    def workflow_setter(self, wf):
        self._workflow = json.dumps(wf.__dict__() ensure_ascii=False)

