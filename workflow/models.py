# -*- coding: utf-8 -*-

from django.db import models
from fields import WorkflowField

class Workflow(models.Model):
    name = models.CharField(max_length=256, unique=True)
    workflow = WorkflowField()
