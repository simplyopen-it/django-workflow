# -*- coding: utf-8 -*-
# pylint: disable=E1101
from django.db import models
from workflow.fields import WorkflowField
from django.utils.log import getLogger
# from django.contrib.aderit.generic_utils.middleware import get_current_user
from simplyopen.middleware import get_current_user
from workflow import managers
# South introspection rules for non standard fields
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        [],
        ["^workflow.fields.WorkflowField"],
     )


logger = getLogger("workflow.models")


class Workflow(models.Model):
    name = models.CharField(max_length=256, unique=True)
    workflow = WorkflowField()

    objects = managers.WorkflowManager()

    def __unicode__(self):
        return unicode(self.name)

    def __getattr__(self, attr):
        return getattr(self.workflow, attr)

    def __getitem__(self, item):
        return self.workflow[item]

    def has_permission(self, user, status):
        groupset = set([group.name for group in user.groups.all()])
        roles = self.workflow[status].roles
        if len(roles) == 0 or groupset.intersection(roles):
            return True
        return False

    def can_travel(self, status_in, status_out):
        return status_in in self.workflow[status_out].incoming.keys()

    def iterarchs(self, user=None):
        for arch in self.workflow.iterarchs():
            if user is not None and self.has_permission(user, arch[1]):
                yield arch

    def archs(self, user=None):
        return [arch for arch in self.iterarchs(user)]


class WorkflowUser(models.Model):
    status = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.workflow is not None and self.status is None:
            self.status = self.workflow.head.name
        super(WorkflowUser, self).save(*args, **kwargs)

    def allowed_statuses(self):
        user = get_current_user()
        ret = self.workflow[self.status].outcoming
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
