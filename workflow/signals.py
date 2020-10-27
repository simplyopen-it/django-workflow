<<<<<<< HEAD
# pylint: disable=unused-argument
from __future__ import unicode_literals

import six
=======
from __future__ import absolute_import
>>>>>>> 4c1d3b3174fe651befc31834aeccdecf80a3d5eb
from django.db.models import signals, Q
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

import six

from .models import (
    WorkflowNode,
    Workflow,
    get_travel_codename,
    get_visit_codename,
)


@receiver(signals.post_save, sender=Workflow)
def create_wf_permissions(instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(Workflow)
        Permission.objects.get_or_create(codename=get_visit_codename(instance),
                                         name='Can visit %s' % six.text_type(instance),
                                         content_type=content_type)

@receiver(signals.post_delete, sender=Workflow)
def delete_wf_permissions(instance, **kwargs):
    content_type = ContentType.objects.get_for_model(Workflow)
    Permission.objects.filter(codename=get_visit_codename(instance),
                              content_type=content_type).delete()

@receiver(signals.post_save, sender=WorkflowNode)
def create_node_permissions(instance, created, **kwargs):
<<<<<<< HEAD
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    Permission.objects.get_or_create(codename=get_travel_codename(instance),
                                     name="Can travel to %s" % six.text_type(instance),
                                     content_type=content_type)
    Permission.objects.get_or_create(codename=get_visit_codename(instance),
                                     name="Can visit %s" % six.text_type(instance),
                                     content_type=content_type)
=======
    if created:
        content_type = ContentType.objects.get_for_model(WorkflowNode)
        Permission.objects.get_or_create(codename=get_travel_codename(instance),
                                         name="Can travel to %s" % six.text_type(instance),
                                         content_type=content_type)
        Permission.objects.get_or_create(codename=get_visit_codename(instance),
                                         name="Can visit %s" % six.text_type(instance),
                                         content_type=content_type)
>>>>>>> 4c1d3b3174fe651befc31834aeccdecf80a3d5eb

@receiver(signals.post_delete, sender=WorkflowNode)
def delete_node_permissions(instance, **kwargs):
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    Permission.objects.filter(Q(codename=get_travel_codename(instance)) | \
                              Q(codename=get_visit_codename(instance)),
                              content_type=content_type).delete()
