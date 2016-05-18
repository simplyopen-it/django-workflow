# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.text import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import Group
from django_extensions.db.fields.json import JSONField
from . import managers

TRAVEL_PREFIX = 'travelto_'
VISIT_PREFIX = 'visit_'


class WorkflowException(ValueError): pass


@python_2_unicode_compatible
class Workflow(models.Model):
    ''' An oriented graph to use as Workflow '''
    name = models.CharField(max_length=256, unique=True)
    head = models.ForeignKey('WorkflowNode', null=True, blank=True, related_name='+',
                             on_delete=models.SET_NULL)

    objects = managers.WorkflowManager()

    def __str__(self):
        return self.name

    def __getitem__(self, item):
        try:
            return self.nodes.get(name=item)
        except WorkflowNode.DoesNotExist:
            raise KeyError(item)

    def get(self, value, default=None):
        try:
            return self[value]
        except KeyError:
            return default

    def bf_walk(self):
        ''' Traverse the workflow in a breadth-first walk '''
        q = [self.head]
        marked = {self.head.pk: True}
        yield self.head
        while len(q) > 0:
            curr = q.pop()
            for elem in curr.outcomings.all().iterator():
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
        for node_name in self.nodes.all().values('name').itervalues():
            yield node_name['name']

    def has_permission(self, user, status):
        codename = 'workflow.%s%s' % (TRAVEL_PREFIX, slugify(unicode(self[status])))
        return user.has_perm(codename)

    def can_travel(self, status_in, status_out):
        return self.nodes.get(name=status_out).incomings.filter(name=status_in).exists()

    def iterarchs(self, user=None):
        for src in self.nodes.all().iterator():
            for dest in src.outcomings.all().iterator():
                if (user is not None) and (not self.has_permission(user, dest.name)):
                    continue
                yield (src.name, dest.name)

    def archs(self, user=None):
        return [arch for arch in self.iterarchs(user)]


@python_2_unicode_compatible
class WorkflowNode(models.Model):
    ''' A workflow node '''
    name = models.SlugField(db_index=True)
    label = models.CharField(max_length=200)
    online = models.SlugField(null=True, blank=True)
    roles = models.ManyToManyField(Group, blank=True)
    attrs = JSONField(default='{}')
    incomings = models.ManyToManyField(
        'self', blank=True,
        related_name='outcomings',
        related_query_name='outcoming',
        symmetrical=False)
    workflow = models.ForeignKey(Workflow, related_name='nodes', related_query_name='node')

    class Meta: # pylint: disable=W0232
        unique_together = ('name', 'workflow')

    def __str__(self):
        return ' '.join([self.workflow.name, self.name])


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
                self.status = self.workflow.head.name
            elif self.status not in self.workflow.keys():
                raise WorkflowException('Invalid status %s' % self.status)
        super(WorkflowModel, self).save(*args, **kwargs)

    def allowed_statuses(self, user=None):
        ''' Return a dictionary of all statuses recheabe from the current one.
        If user is specified, alse take into account user permissions.
        '''
        if user is not None:
            return dict([(node.name, node) for node in self.workflow[self.status].outcomings.all()
                         if user.has_perm('workflow.%s%s' % (TRAVEL_PREFIX, slugify(unicode(node))))])
        return dict([(node.name, node) for node in self.workflow[self.status].outcomings.all()])

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
