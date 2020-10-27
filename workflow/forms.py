# -*- coding: utf-8 -*-
from __future__ import absolute_import
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
                 empty_permitted=False, instance=None, use_required_attribute=None,
                 *args, **kwargs):
        if initial is None:
            initial = {}
        if instance is not None:
            initial.update({
                'outcomings': instance.outcomings,
            })
        try:
            super(WorkflowNodeForm, self).__init__(
                data=data, files=files, auto_id=auto_id, prefix=prefix,
                initial=initial, error_class=error_class, label_suffix=label_suffix,
                empty_permitted=empty_permitted, instance=instance,
                use_required_attribute=use_required_attribute,
                *args, **kwargs
            )
        except TypeError:
            # Without 'use_required_attribute'
            super(WorkflowNodeForm, self).__init__(
                data=data, files=files, auto_id=auto_id, prefix=prefix,
                initial=initial, error_class=error_class, label_suffix=label_suffix,
                empty_permitted=empty_permitted, instance=instance,
                *args, **kwargs
            )
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
