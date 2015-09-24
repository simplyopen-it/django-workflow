# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.db import models, migrations, connection
import django_extensions.db.fields.json
from workflow import graph

def json2db(apps, schema_editor):
    Workflow = apps.get_model('workflow', 'Workflow')
    Group = apps.get_model('auth', 'Group')
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    # We need to use raw SQL because 'workflow' is both a table field
    # and a class method at this stage.
    query = '''SELECT * from workflow_workflow'''
    with connection.cursor() as cr:
        cr.execute(query)
        results = cr.cursor.fetchall()
    for _, name, workflow, _ in results:
        wf = Workflow.objects.get(name=name)
        wf_dict = json.loads(workflow)
        wf_graph = graph.Graph.parse(wf_dict)
        for node in wf_graph.itervalues():
            wf_node = WorkflowNode.objects.create(
                name=node.name,
                label=node.label,
                online=node.online,
                workflow=wf)
            wf_node.roles.add(*Group.objects.filter(name__in=node.roles))
            if node.name == wf_graph.head.name:
                wf.head=wf_node
                wf.save()
        for out, _in in wf_graph.iterarchs():
            WorkflowNode.objects.get(name=_in, workflow=wf).incomings.add(
                WorkflowNode.objects.get(name=out, workflow=wf))


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField(db_index=True)),
                ('label', models.CharField(max_length=200)),
                ('online', models.SlugField(null=True, blank=True)),
                ('attrs', django_extensions.db.fields.json.JSONField(blank=True)),
                ('incomings', models.ManyToManyField(related_name='incomings_rel_+', to='workflow.WorkflowNode', blank=True)),
                ('roles', models.ManyToManyField(to='auth.Group', blank=True)),
                ('workflow', models.ForeignKey(to='workflow.Workflow')),
            ],
            options={
                'unique_together': ('name', 'workflow'),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='workflow',
            name='head',
            field=models.ForeignKey(to='workflow.WorkflowNode', null=True, blank=True, related_name='+',
                                    on_delete=models.SET_NULL)
        ),
        migrations.RunPython(json2db),
        migrations.RemoveField(
            model_name='workflow',
            name='workflow',
        ),
    ]
