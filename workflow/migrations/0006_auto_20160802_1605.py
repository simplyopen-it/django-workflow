# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def data_foreward(apps, schema_editor):
    Workflow = apps.get_model('workflow', 'Workflow')
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    for wf in Workflow.objects.all().iterator():
        wf.head_new = wf.head.name
        wf.save()
    for wfn in WorkflowNode.objects.all().iterator():
        wfn.outcomings_new = list(wfn.outcomings.all().values_list('name', flat=True))
        wfn.save()

def data_backward(apps, schema_editor):
    Workflow = apps.get_model('workflow', 'Workflow')
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    for wf in Workflow.objects.all().iterator():
        wf.head = WorkflowNode.objects.get(workflow=wf, name=wf.head_new)
        wf.save()
    for wfn in WorkflowNode.objects.all().iterator():
        wfn.outcomings.add(*WorkflowNode.objects.filter(workflow=wfn.workflow, name__in=wfn.outcomings_new))


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0005_auto_20160802_1539'),
    ]

    operations = [
        migrations.RunPython(data_foreward, data_backward),
    ]
