# -*- coding: utf-8 -*-
from django.db import models
from fields import WorkflowField
from django.utils.log import getLogger
from django.contrib.aderit.generic_utils.middleware import get_current_user

logger = getLogger("workflow.models")

class Workflow(models.Model):
    name = models.CharField(max_length=256, unique=True)
    workflow = WorkflowField()

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


class WorkflowUser(models.Model):
    status = models.CharField(max_length=255)
    workflow = models.ForeignKey(Workflow)

    class Meta:
        abstract = True

    def can_travel(self, target):
        return self.workflow.can_travel(self.status, target)

    def get_status(self):
        return self.workflow[self.status]

    def set_online_status(self, status, *args, **kwargs):
        return status

    def set_status(self, status, *args, **kwargs):
        if not self.can_travel(status):
            e = RuntimeError(
                "Can not change from status '%s' to '%s'" % \
                (self.status, status))
            logger.warning(e)
            raise e
        user = get_current_user()
        if not self.workflow.has_permission(user, status):
            e = RuntimeError(
                "You don't have ther permission to switch to status '%s'" % \
                status)
            logger.warning(e)
            raise e
        if self.get_status().outcoming[status].online is not None:
            status = self.set_online_status(status, *args, **kwargs)
        self.status = status
