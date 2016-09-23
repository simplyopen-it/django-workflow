# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import workflow.fields


class Migration(migrations.Migration):

    operations = [
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
                ('head', models.SlugField(default='', blank=True)),
            ],
            options={
                'permissions': (('force_status', 'Can force workflow status'),),
            },
        ),
        migrations.CreateModel(
            name='WorkflowNode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.SlugField()),
                ('label', models.CharField(max_length=200)),
                ('outcomings', workflow.fields.JSONListUniqueField(default=list)),
                ('workflow', models.ForeignKey(related_query_name='node', related_name='nodes', to='workflow.Workflow')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='workflownode',
            unique_together=set([('name', 'workflow')]),
        ),
    ]
