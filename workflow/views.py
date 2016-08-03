from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied
from .models import get_travel_codename


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
