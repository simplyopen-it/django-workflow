# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_extensions.db.fields.json
from django.utils.text import slugify
from ..models import TRAVEL_PREFIX, VISIT_PREFIX

def create_wf_permissions(apps, schema_editor):
    Workflow = apps.get_model('workflow', 'Workflow')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(Workflow)
    for wf in Workflow.objects.all().values('name').iterator():
        Permission.objects.create(codename='%s%s' % (VISIT_PREFIX, slugify(wf['name'])),
                                  name="Can Visit %s" % wf['name'],
                                  content_type=content_type)

def delete_wf_permissions(apps, shcema_editor):
    Workflow = apps.get_model('workflow', 'Workflow')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(Workflow)
    Permission.objects.filter(codename__startswith=VISIT_PREFIX,
                              content_type=content_type).delete()

def create_node_permissions(apps, schema_editor):
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    for node in WorkflowNode.objects.all().values_list('workflow__name', 'name'):
        node_unicode = ' '.join(node)
        Permission.objects.create(codename='%s%s' % (TRAVEL_PREFIX, slugify(node_unicode)),
                                  name="Can travel to %s" % node_unicode,
                                  content_type=content_type)
        Permission.objects.create(codename='%s%s' % (VISIT_PREFIX, slugify(node_unicode)),
                                  name="Can visit %s" % node_unicode,
                                  content_type=content_type)

def delete_node_permissions(apps, schema_editor):
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    Permission.objects.filter(models.Q(codename__startswith=TRAVEL_PREFIX) | \
                              models.Q(codename__startswith=VISIT_PREFIX),
                              content_type=content_type).delete()

def assign_permissions(apps, schema_editor):
    # We consider only 'travelto' permissions because 'visit' is not
    # completely implemented yet.
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    for group in Group.objects.all():
        nodes = WorkflowNode.objects.filter(roles=group).values_list('workflow__name', 'name')
        codenames = ['%s%s' % (TRAVEL_PREFIX, slugify(' '.join(node)))
                     for node in nodes]
        permissions = Permission.objects.filter(codename__in=codenames)
        group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20150922_1401'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workflow',
            options={'permissions': (('force_status', 'Can force workflow status'),)},
        ),
        migrations.AlterField(
            model_name='workflownode',
            name='attrs',
            field=django_extensions.db.fields.json.JSONField(),
        ),
        migrations.AlterField(
            model_name='workflownode',
            name='incomings',
            field=models.ManyToManyField(related_query_name='outcoming', related_name='outcomings', to='workflow.WorkflowNode', blank=True),
        ),
        migrations.AlterField(
            model_name='workflownode',
            name='workflow',
            field=models.ForeignKey(related_query_name='node', related_name='nodes', to='workflow.Workflow'),
        ),
        migrations.AlterUniqueTogether(
            name='workflownode',
            unique_together=set([('name', 'workflow')]),
        ),
        migrations.RunPython(create_wf_permissions, delete_wf_permissions),
        migrations.RunPython(create_node_permissions, delete_node_permissions),
        migrations.RunPython(assign_permissions, migrations.RunPython.noop),
    ]
