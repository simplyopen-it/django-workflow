from __future__ import unicode_literals

import json
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db import transaction
from django.db.models.query import QuerySet
from .models import get_travel_codename


class BaseStatusView(View):
    ''' Set the status of a WorkflowModel instance and redirect to
    'success_url'.
    '''

    data_var = 'data'
    success_url = ''
    model = None
    queryset = None

    def get_queryset(self, *args, **kwargs):
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.select_for_update().all()
        elif self.model is not None:
            queryset = self.model._default_manager.select_for_update().filter(*args, **kwargs) # pylint: disable=W0212
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {
                    'cls': self.__class__.__name__
                }
            )
        return queryset

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.get(self.data_var, '[]'))
        with transaction.atomic():
            self.queryset = self.get_queryset(pk__in=data.keys())
            for obj in self.queryset.iterator():
                self.set_status(obj, **data[str(obj.pk)])
                obj.save()
        return self.get_response()

    def set_status(self, obj, status, force=False, **kwargs):
        node = obj.workflow[status]
        if force:
            if not self.request.user.has_perm('workflow.force_status'):
                raise PermissionDenied("You are not allowed to force statuses")
            obj.status = status
        elif not self.request.user.has_perm(get_travel_codename(node)):
            raise PermissionDenied("You are not allowed to change staus from '%(from)s to '%(to)s'" % {
                'from': obj.status,
                'to': status})
        else:
            obj.set_status(status, **kwargs)

    def get_success_url(self):
        return self.success_url

    def get_response(self):
        return HttpResponseRedirect(self.get_success_url())
