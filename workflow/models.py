# -*- coding: utf-8 -*-
from django.db import models
from django.utils.log import getLogger
from django.contrib.auth.models import Group
from django_extensions.db.fields.json import JSONField
from simplyopen.middleware import get_current_user
from workflow import managers


logger = getLogger("workflow.models")


class Workflow(models.Model):
    ''' An oriented graph to use as Workflow '''
    name = models.CharField(max_length=256, unique=True)
    head = models.ForeignKey('WorkflowNode', null=True, blank=True, related_name='+',
                             on_delete=models.SET_NULL)

    objects = managers.WorkflowManager()

    def __unicode__(self):
        return unicode(self.name)

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

    @property
    def workflow(self):
        # For compatibility
        return self

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
        for node in self.itervalues():
            yield node.name

    def get_nodes_by_roles(self, roles):
        return self.nodes.filter(roles__name__in=roles)

    def has_permission(self, user, status):
        roles = set(self.nodes.get(name=status).roles.all())
        return len(roles) == 0 or set(user.groups.all()).intersection(roles)

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

    class Meta:                 # pylint: disable=W0232
        unique_together = ('name', 'workflow')

    def __unicode__(self):
        return self.workflow.name + '/' + self.name

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def outcoming(self):
        return dict([(node.name, node) for node in self.outcomings.all()])

    def incoming(self):
        return dict([(node.name, node) for node in self.incomings.all()])


class WorkflowUser(models.Model):
    status = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow)

    class Meta:                 # pylint: disable=W0232
        abstract = True

    def save(self, *args, **kwargs):
        if self.workflow is not None and self.status is None:
            self.status = self.workflow.head.name
        super(WorkflowUser, self).save(*args, **kwargs)

    def allowed_statuses(self):
        user = get_current_user()
        ret = dict([(node.name, node) for node in self.workflow[self.status].outcomings.all()])
        if user is not None:
            roles = set([group.name for group in user.groups.all()])
            allowed_by_role = [node.name for node in
                               self.workflow.get_nodes_by_roles(roles)]
            for key in ret.keys():
                if key not in allowed_by_role:
                    ret.pop(key, None)
        return ret

    def can_travel(self, target):
        return self.workflow.can_travel(self.status, target)

    def get_status(self):
        return self.workflow[self.status]

    def set_online_status(self, status, *args, **kwargs):
        return status

    def set_status(self, status, *args, **kwargs):
        if not self.can_travel(status):
            e = RuntimeError(
                "%s with id %s; Can not change from status '%s' to '%s'" % \
                (self._meta.object_name, self.pk, self.status, status))
            logger.warning(e)
            raise e
        user = get_current_user()
        if user is not None and not self.workflow.has_permission(user, status):
            e = RuntimeError(
                "%s does not have the permission to switch to status '%s'" % \
                (user, status))
            logger.warning(e)
            raise e
        target_obj = self.workflow[status]
        if target_obj.online is not None:
            status = self.set_online_status(target_obj.online, *args, **kwargs)
        self.status = status
