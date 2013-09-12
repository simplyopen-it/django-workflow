# -*- coding: utf-8 -*-
from django.utils.log import getLogger
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from django.forms import forms, fields, widgets
from django.core.exceptions import ValidationError

from workflow.models import Workflow

logger = getLogger('workflow.ajax')


class NodeForm(forms.Form):
    node_name = fields.CharField()
    # online = fields.CharField()
    out_names = fields.CharField(required=False)
    in_names = fields.CharField(required=False)



@dajaxice_register
def delnode(request, object_id, nodename):
    dajax = Dajax()
    w = Workflow.objects.get(id=int(object_id))
    w.workflow.del_node(name=nodename)
    w.save()
    dajax.script('window.location.reload();')
    return dajax.json()

@dajaxice_register
def addnode(request, object_id, form):
    dajax = Dajax()
    form = NodeForm(deserialize_form(form))
    if not form.errors:
        w = Workflow.objects.get(id=int(object_id))
        w.workflow.add_node(name=form.cleaned_data.get('node_name'))
        w.save()
    dajax.script('window.location.reload();')
    return dajax.json()

@dajaxice_register
def add_out(request, object_id, nodename, new_out):
    dajax = Dajax()
    if new_out:
        w = Workflow.objects.get(id=int(object_id))
        w.workflow.add_node(name=new_out)
        w.save()
        w.workflow.add_arch(name_out=nodename, name_in=new_out)
        w.save()
    dajax.script('window.location.reload();')
    return dajax.json()

@dajaxice_register
def add_in(request, object_id, nodename, new_in):
    dajax = Dajax()
    if new_in:
        w = Workflow.objects.get(id=int(object_id))
        w.workflow.add_node(name=new_in)
        w.save()
        w.workflow.add_arch(name_out=new_in, name_in=nodename)
        w.save()
    dajax.script('window.location.reload();')
    return dajax.json()

@dajaxice_register
def remove_out(request, object_id, nodename, arch_out):
    dajax = Dajax()
    if arch_out:
        w = Workflow.objects.get(id=int(object_id))
        w.workflow.del_arch(name_out=nodename, name_in=arch_out)
        w.save()
    dajax.script('window.location.reload();')
    return dajax.json()

@dajaxice_register
def remove_in(request, object_id, nodename, arch_in):
    dajax = Dajax()
    if arch_in:
        w = Workflow.objects.get(id=int(object_id))
        w.workflow.del_arch(name_out=arch_in, name_in=nodename)
        w.save()
    dajax.script('window.location.reload();')
    return dajax.json()
