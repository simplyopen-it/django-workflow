# -*- coding: utf-8 -*-
from django import forms
from django.contrib.admin import widgets as admin_widgets
from workflow.models import WorkflowNode, Workflow


class WorkflowForm(forms.ModelForm):

    class Meta:                 # pylint: disable=W0232
        model = Workflow
        fields = '__all__'

    def __init__(self, data=None, files=None, instance=None, *args, **kwargs):
        super(WorkflowForm, self).__init__(data=data, files=files, instance=instance, *args, **kwargs)
        if instance is not None:
            self.fields['head'].queryset = instance.nodes.all()
        else:
            self.fields['head'].queryset = WorkflowNode.objects.none()



class WorkflowNodeForm(forms.ModelForm):

    class Meta:                 # pylint: disable=W0232
        model = WorkflowNode
        fields = [
            'name',
            'label',
            'online',
            'roles',
            'incomings',
        ]
        widgets = {
            'incomings': admin_widgets.FilteredSelectMultiple('Incomings', False),
            'roles': admin_widgets.FilteredSelectMultiple('Roles', False),
        }

    def __init__(self, data=None, files=None, instance=None, *args, **kwargs):
        super(WorkflowNodeForm, self).__init__(data=data, files=files, instance=instance, *args, **kwargs)
        if instance is not None:
            self.fields['incomings'].queryset = instance.workflow.nodes.exclude(pk=instance.pk)
        else:
            self.fields['incomings'].queryset = Workflow.objects.none()
