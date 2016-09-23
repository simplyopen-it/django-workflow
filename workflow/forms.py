# -*- coding: utf-8 -*-
from django import forms
from django.forms.utils import ErrorList
from django.contrib.admin import widgets as admin_widgets
from workflow.models import WorkflowNode, Workflow


class WorkflowForm(forms.ModelForm):
    head = forms.ChoiceField(choices=list, required=False)

    class Meta:                 # pylint: disable=W0232
        model = Workflow
        fields = '__all__'

    def __init__(self, data=None, files=None, instance=None, *args, **kwargs):
        super(WorkflowForm, self).__init__(data=data, files=files, instance=instance, *args, **kwargs)
        if instance is not None:
            self.fields['head'].choices = instance.nodes.values_list('name', 'label')


class WorkflowNodeForm(forms.ModelForm):
    outcomings = forms.MultipleChoiceField(
        choices=tuple(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple('Outcomings', False))

    class Meta:                 # pylint: disable=W0232
        model = WorkflowNode
        fields = [
            'name',
            'label',
        ]

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None):
        if initial is None:
            initial = {}
        if instance is not None:
            initial.update({
                'outcomings': instance.outcomings,
            })
        super(WorkflowNodeForm, self).__init__(
            data=data, files=files, auto_id=auto_id, prefix=prefix,
            initial=initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=instance)
        if instance is not None:
            self.fields['outcomings'].choices = instance.workflow.nodes.values_list('name', 'label')

    def save(self, commit=True):
        if not self.cleaned_data.get('outcomings', []):
            self.instance.outcomings = []
        return super(WorkflowNodeForm, self).save(commit=commit)


class WorkflowNodeAdminForm(WorkflowNodeForm):

    class Meta:                 # pylint: disable=W0232
        model = WorkflowNode
        fields = [
            'workflow',
            'name',
            'label',
        ]
