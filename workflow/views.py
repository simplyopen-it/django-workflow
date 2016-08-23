import tempfile
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View, DetailView
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied
from . import dot
from .models import (
    get_travel_codename,
    Workflow,
)


class WorkflowPreviewView(DetailView):

    model = Workflow

    def render_to_response(self, context, **kwargs):
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = 'attachment;filename=%s.png' % self.object.name
        # pydot in testing is patched to accept file-like objects but
        # the upstream is not that clever, if we want to make this app
        # porta
        dot.plot(self.object, response)
        return response


class SetStatusView(SingleObjectMixin, View):

    status_var = 'status'
    success_url = ''

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        status = kwargs.get(self.status_var)
        self.set_status(request, status)
        return self.get_response()

    def set_status(self, request, status):
        if not request.user.has_perm(get_travel_codename(status)):
            raise PermissionDenied()
        self.object.set_status(status)

    def get_response(self):
        return HttpResponseRedirect(reverse(self.success_url))
