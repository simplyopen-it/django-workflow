from __future__ import unicode_literals

import tempfile
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View, DetailView
from django.views.generic.list import MultipleObjectMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
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


class BaseStatusView(MultipleObjectMixin, View):
    ''' Set the status of a WorkflowModel instance and redirect to
    'success_url'.
    '''
    success_url = ''

    def get_queryset(self):
        return super(BaseStatusView, self).get_queryset().select_for_update()

    def post(self, request,  *args, **kwargs):
        status = request.POST.get('status')
        force = request.POST.get('force', False)
        with transaction.atomic():
            # Status changes are made in a transaction block with serializable
            # isolation because they depend on the current status.
            self.queryset = self.get_queryset()
            for obj in self.queryset.iterator():
                self.set_status(obj, status=status, force=force)
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
