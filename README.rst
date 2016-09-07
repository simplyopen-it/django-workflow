===============
django-workflow
===============

Overview
********

``workflow`` is a Django application that provide a basic system to manage status changes for model's objects.

Often times there's the need to define models which instances should evolve through a specified path in a graph, a workflow.

Basic Usage
***********

As you may expect a workflow is a collection of nodes and arcs that link them together.

``WorkflowModel`` is an abstract model class that provide the basic fields and methods to make your model's instances use the related ``Workflow``.

Views
*****

Signals
*******
