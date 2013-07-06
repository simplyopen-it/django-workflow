# -*- coding: utf-8 -*-
from django.contrib import admin
from models import Workflow

class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(Workflow, WorkflowAdmin)
