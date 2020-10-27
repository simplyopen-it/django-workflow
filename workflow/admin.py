# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

from django.conf.urls import url
try:
    from django.core.urlresolvers import reverse, NoReverseMatch
except ImportError:
    from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.contrib import admin
from django.contrib.admin.decorators import register
from .forms import (
    WorkflowNodeForm,
    WorkflowNodeAdminForm,
    WorkflowForm,
)
from .models import (
    Workflow,
    WorkflowNode,
)
from .views import WorkflowPreviewView


class WorkflowNodeInline(admin.StackedInline):
    model = WorkflowNode
    form = WorkflowNodeForm
    extra = 0
    max_num = None
    can_delete = True
    fields = (
        ('name', 'label'),
        'outcomings',
    )


@register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    form = WorkflowForm
    fieldsets = [
        (None, {
            'fields': (
                'name',
                'head',
                'preview',
            ),
        }),
    ]
    list_display = (
        'name',
    )
    readonly_fields = (
        'preview',
    )
    inlines = (
        WorkflowNodeInline,
    )

    def get_urls(self):
        urls = super(WorkflowAdmin, self).get_urls()
        urls.append(url(r'workflow/preview/(?P<pk>[0-9]+)$',
                        self.admin_site.admin_view(WorkflowPreviewView.as_view()),
                        name='workflow_preview'))
        return urls

    def preview(self, instance):
        if not instance.pk:
            return
        try:
            from . import dot # pylint: disable=unused-variable
        except ImportError:
            return "Preview not available, install python-pydot."
        try:
            href = reverse('admin:workflow_preview', kwargs={'pk': instance.pk})
        except NoReverseMatch:
            return 'Preview not available yet.'
        return format_html('<a href="{}">Preview</a>'.format(href))


@register(WorkflowNode)
class WorkflowNodeAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {
            'fields': (
                'workflow',
                'name',
                'label',
                'outcomings',
            ),
        }),
        ('Close Nodes', {
            'fields': (
                ('pretty_incomings', 'pretty_outcomings'),
            ),
        }),
    ]
    list_display= (
        'name',
        'workflow',
        'pretty_incomings',
        'pretty_outcomings',
    )
    readonly_fields = (
        'pretty_incomings',
        'pretty_outcomings',
    )
    form = WorkflowNodeAdminForm
    list_filter = (
        'workflow',
    )
    search_fields = (
        'name',
        'label',
    )

    def _pretty_proximity_list(self, instance, direction):
        out = ['<ul>']
        close_nodes = WorkflowNode.objects.filter(workflow=instance.workflow, name__in=getattr(instance, direction))
        for node in close_nodes.iterator():
            out.append('<li><a href="%(href)s">%(label)s</a></li>' % {
                'label': node.label,
                'href': reverse('admin:workflow_workflownode_change', args=(node.pk,))})
        out.append('</ul>')
        return format_html(''.join(out))

    def pretty_outcomings(self, instance):
        return self._pretty_proximity_list(instance, 'outcomings')
    pretty_outcomings.short_description = 'Outcomings'

    def pretty_incomings(self, instance):
        return self._pretty_proximity_list(instance, 'incomings')
    pretty_incomings.short_description = 'Incomings'
