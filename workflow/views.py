from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from .models import get_travel_codename


class BaseStatusView(SingleObjectMixin, View):
    ''' Set the status of a WorkflowModel instance and redirect to
    'success_url'.
    '''

    status_var = 'status'
    success_url = ''

    def __init__(self, *args, **kwargs):
        super(BaseStatusView, self).__init__(*args, **kwargs)
        self.object = None
        self.force = False

    def get_queryset(self):
        qs = super(BaseStatusView, self).get_queryset()
        # Prevent race conditions on set_status
        return qs.select_for_update().prefetch_related('workflow')

    def post(self, request, *args, **kwargs):
        status = request.POST.get(self.status_var)
        self.force = request.POST.get('force', False)
        with transaction.atomic():
            self.object = self.get_object()
            self.set_status(status)
            self.object.save()
        return self.get_response()

    def set_status(self, status, **kwargs):
        node = self.object.workflow[status]
        if self.force:
            if not self.request.user.has_perm('workflow.force_status'):
                raise PermissionDenied("You are not allowed to force statuses")
            self.object.status = status
        elif not self.request.user.has_perm(get_travel_codename(node)):
            raise PermissionDenied("You are not allowed to change staus from '%(from)s to '%(to)s'" % {
                'from': self.object.status,
                'to': status})
        else:
            self.object.set_status(status, **kwargs)

    def get_success_url(self):
        return self.success_url

    def get_response(self):
        return HttpResponseRedirect(self.get_success_url())
