# -*- coding: utf-8 -*-
from django import forms
from django.forms.utils import ErrorList
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

    outcomings = forms.models.ModelMultipleChoiceField(
        WorkflowNode.objects.none(),
        required=False,
        widget=admin_widgets.FilteredSelectMultiple('Outcomings', False)
    )

    class Meta:                 # pylint: disable=W0232
        model = WorkflowNode
        fields = [
            'name',
            'label',
            'online',
            'roles',
            'incomings',
        ]

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=None,
                 empty_permitted=False, instance=None):
        if initial is None:
            initial = {}
        if instance is not None:
            initial.update({
                'outcomings': instance.outcomings.all(),
            })
        super(WorkflowNodeForm, self).__init__(
            data=data, files=files, auto_id=auto_id, prefix=prefix,
            initial=initial, error_class=error_class, label_suffix=label_suffix,
            empty_permitted=empty_permitted, instance=instance)
        if instance is not None:
            self.fields['incomings'].queryset = instance.workflow.nodes.exclude(pk=instance.pk)
            self.fields['outcomings'].queryset = instance.workflow.nodes.exclude(pk=instance.pk)
        else:
            self.fields['incomings'].queryset = Workflow.objects.none()


    def save(self, commit=True):
        instance = super(WorkflowNodeForm, self).save(commit=commit)
        try:
            instance.outcomings.clear()
            instance.outcomings.add(*self.cleaned_data.get('outcomings'))
        except ValueError:
            pass
        return instance
