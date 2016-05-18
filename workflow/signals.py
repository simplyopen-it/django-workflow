from django.utils.text import slugify
from django.db.models import signals, Q
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import WorkflowNode

@receiver(signals.post_save, sender=WorkflowNode)
def create_node_permissions(instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(WorkflowNode)
        Permission.objects.get_or_create(codename='travelto_%s' % slugify(unicode(instance)),
                                         name="Can travel to %s" % unicode(instance),
                                         content_type=content_type)
        Permission.objects.get_or_create(codename='visit_%s' % slugify(unicode(instance)),
                                         name="Can visit to %s" % unicode(instance),
                                         content_type=content_type)

@receiver(signals.post_delete, sender=WorkflowNode)
def delete_node_permissions(instance, **kwargs):
    content_type = ContentType.objects.get_for_model(WorkflowNode)
    Permission.objects.filter(Q(codename='travelto_%s' % slugify(unicode(instance))) | \
                              Q(codename='visit_%s' % slugify(unicode(instance))),
                              content_type=content_type).delete()
