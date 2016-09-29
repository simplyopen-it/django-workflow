# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from . import fields
from . import managers

TRAVEL_PREFIX = 'travelto_'
VISIT_PREFIX = 'visit_'

def get_travel_codename(node):
    return 'workflow.%s%s' % (TRAVEL_PREFIX, slugify(unicode(node)))

def get_visit_codename(node):
    return 'workflow.%s%s' % (VISIT_PREFIX, slugify(unicode(node)))


class WorkflowException(ValueError): pass


@python_2_unicode_compatible
class Workflow(models.Model):
    ''' An oriented graph to use as Workflow '''
    name = models.CharField(max_length=256, unique=True)
    head = models.SlugField(blank=True, default='')

    objects = managers.WorkflowManager()

    class Meta:  # pylint: disable=W0232
        permissions = (
            ('force_status', 'Can force workflow status'),
        )

    def __str__(self):
        return self.name

    def __getitem__(self, item):
        try:
            return self.nodes.get(name=item)
        except WorkflowNode.DoesNotExist:
            raise KeyError(item)

    def natural_key(self):
        return (self.name,)

    def get(self, value, default=None):
        try:
            return self[value]
        except KeyError:
            return default

    def get_head(self):
        return self.get(self.head)

    def bf_walk(self):
        ''' Traverse the workflow in a breadth-first walk '''
        head = WorkflowNode.objects.get(name=self.head, workflow=self)
        q = [head]
        marked = {head.pk: True}
        yield head
        while len(q) > 0:
            curr = q.pop()
            for elem in self.nodes.filter(name__in=curr.outcomings).iterator():
                if not marked.get(elem.pk, False):
                    marked[elem.pk] = True
                    q.insert(0, elem)
                    yield elem

    def itervalues(self):
        return self.nodes.all().iterator()

    def values(self):
        return [value for value in self.itervalues()]

    def keys(self):
        return [key for key in self.iterkeys()]

    def iterkeys(self):
        return self.nodes.values_list('name', flat=True).iterator()

    def has_permission(self, user, status):
        codename = get_travel_codename(self[status])
        return user.has_perm(codename)

    def can_travel(self, status_in, status_out):
        return status_out in self.nodes.get(name=status_in).outcomings

    def iterarchs(self, user=None):
        for src in self.nodes.all().iterator():
            for dest_name in iter(src.outcomings):
                if (user is not None) and (not self.has_permission(user, dest_name)):
                    continue
                yield (src.name, dest_name)

    def archs(self, user=None):
        return [arch for arch in self.iterarchs(user)]


@python_2_unicode_compatible
class WorkflowNode(models.Model):
    ''' A workflow node '''
    name = models.SlugField(db_index=True)
    label = models.CharField(max_length=200)
    outcomings = fields.JSONListUniqueField(default=list)
    workflow = models.ForeignKey(Workflow, related_name='nodes', related_query_name='node')

    objects = managers.WorkflowNodeManager()

    class Meta: # pylint: disable=W0232
        unique_together = ('name', 'workflow')

    def __str__(self):
        return ' '.join([self.workflow.name, self.name])

    def natural_key(self):
        return self.workflow.natural_key() + (self.name,)
    natural_key.dependencies = ['workflow.workflow']

    def _set_incomings(self, values):
        for node in self.workflow.nodes.all().iterator():
            if node.name in values:
                node.outcomings.append(self.name)
            elif self.name in node.outcomings:
                node.outcomings.remove(self.name)
            else:
                continue
            node.save()

    def _get_incomings(self):
        return [node.name for node in self.workflow.nodes.exclude(pk=self.pk)
                if self.name in node.outcomings]

    incomings = property(_get_incomings, _set_incomings)


class WorkflowModel(models.Model):
    ''' An abstract model to make use of workflows.
    '''
    # pylint: disable=E1136
    status = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow)

    class Meta: # pylint: disable=W0232
        abstract = True

    def save(self, *args, **kwargs):
        if self.workflow is not None:
            if self.status is None:
                self.status = self.workflow.head
            elif self.status not in self.workflow.keys():
                raise WorkflowException("Invalid status '%s'" % self.status)
        super(WorkflowModel, self).save(*args, **kwargs)

    def allowed_statuses(self, user=None):
        ''' Return a dictionary of all statuses recheabe from the current one.
        If user is specified, alse take into account user permissions.
        '''
        qs = WorkflowNode.objects.filter(workflow=self.workflow, name__in=self.workflow[self.status].outcomings)
        if user is not None:
            return dict([(node.name, node) for node in qs.iterator()
                         if user.has_perm(get_travel_codename(node))])
        return dict([(node.name, node) for node in qs.iterator()])

    def can_travel(self, target):
        ''' Check if the target status is reacheable from the current status. '''
        return self.workflow.can_travel(self.status, target)

    def get_status(self):
        ''' Return the WornfloNode object for the current status. '''
        return self.workflow[self.status]

    def set_status(self, status, *args, **kwargs):
        ''' Controlled status set. '''
        if not self.can_travel(status):
            raise WorkflowException("Can not travel from '%s' to '%s'" % (self.status, status))
        self.status = status
