# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.text import slugify


def create_permissions(apps, schema_editor):
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    for node in WorkflowNode.objects.all().values('name', 'workflow__name'):
        node_unicode = '/'.join([node['workflow__name'], node['name']])
        Permission.objects.create(codename='travelto_%s' % slugify(node_unicode),
                                  name="Can travel to %s" % node_unicode,
                                  content_type=content_type)
        Permission.objects.create(codename='visit_%s' % slugify(node_unicode),
                                  name="Can visit to %s" % node_unicode,
                                  content_type=content_type)

def delete_permissions(apps, schema_editor):
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    Permission.objects.filter(models.Q(codename__startswith='travelto_') | \
                              models.Q(codename__startswith='visit_'),
                              content_type=content_type).delete()

def assign_permissions(apps, schema_editor):
    # We consider only 'travelto' permissions because 'visit' is not
    # completely implemented yet.
    WorkflowNode = apps.get_model('workflow', 'WorkflowNode')
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    for group in Group.objects.all():
        nodes = WorkflowNode.objects.filter(roles=group).values('name', 'workflow__name')
        codenames = ['travelto_%s' % slugify('/'.join([node['workflow__name'], node['name']]))
                     for node in nodes]
        permissions = Permission.objects.filter(codename__in=codenames)
        group.permissions.add(*permissions)


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20150922_1401'),
    ]

    operations = [
        migrations.RunPython(create_permissions, delete_permissions),
        migrations.RunPython(assign_permissions, migrations.RunPython.noop),
    ]
