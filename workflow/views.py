from __future__ import unicode_literals

import json
import tempfile
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, DetailView
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.db import transaction
from django.db.models.query import QuerySet
from .models import (
    get_travel_codename,
    Workflow,
)


class WorkflowPreviewView(DetailView):

    model = Workflow

    def render_to_response(self, context, **kwargs):
        # pydot not required
        from . import dot
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = 'attachment;filename=%s.png' % self.object.name
        # pydot require a file name, not a file-like object, thus we create a
        # tmp file and copy it into the response.
        with tempfile.NamedTemporaryFile() as buf:
            dot.plot(self.object, buf.name)
            response.write(buf.read())
        return response


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
            # Status changes are made in a transaction block with serializable
            # isolation because they depend on the curent status.
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
