# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.decorators import register
from workflow.forms import WorkflowNodeForm, WorkflowForm
from workflow.models import Workflow, WorkflowNode


class WorkflowNodeInline(admin.StackedInline):
    model = WorkflowNode
    form = WorkflowNodeForm
    extra = 0
    max_num = None
    can_delete = True
    fields = (
        ('name', 'label', 'online'),
        'roles',
        'incomings',
        'outcomings',
    )
    readonly_fields = (
        'outcomings',
    )

    def outcomings(self, instance):
        return ', '.join([node.label for node in instance.outcomings.all()])


@register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    form = WorkflowForm
    fields = (
        'name',
        'head',
    )
    list_display = (
        'name',
    )
    inlines = (
        WorkflowNodeInline,
    )
