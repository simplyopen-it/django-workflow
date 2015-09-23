# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.decorators import register
from workflow import forms
from workflow.models import Workflow, WorkflowNode


class WorkflowNodeInline(admin.StackedInline):
    model = WorkflowNode
    form = forms.WorkflowNodeForm
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
    form = forms.WorkflowForm
    fields = (
        'name',
        'head',
    )
    list_display = (
        'name',
        'head',
    )
    inlines = (
        WorkflowNodeInline,
    )
