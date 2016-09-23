# -*- coding: utf-8 -*-
import os
from django.conf import settings
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
            ),
        }),
        ('Preview', {
             'fields': (
                 'preview',
             ),
             'classes': ('collapse',),
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

    def preview(self, instance):
        try:
            from workflow import dot
        except ImportError:
            return 'module <b>pydot</b> not installed'
        out_file = os.path.join(settings.MEDIA_ROOT, 'workflow', '%s.png' % instance.name)
        if not os.path.isdir(os.path.dirname(out_file)):
            os.makedirs(os.path.dirname(out_file))
        dot.plot(instance, out_file)
        return '<img src="%sworkflow/%s.png">' % (settings.MEDIA_URL, instance.name)
    preview.allow_tags = True


@register(WorkflowNode)
class WorkflowNodeAdmin(admin.ModelAdmin):
    list_display= (
        'name',
        'workflow',
        'outcomings',
    )
    form = WorkflowNodeAdminForm
    list_filter = (
        'workflow',
    )
    search_fields = (
        'name',
        'label',
    )
