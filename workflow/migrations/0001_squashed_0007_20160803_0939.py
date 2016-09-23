# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import workflow.fields


class Migration(migrations.Migration):

    replaces = [(b'workflow', '0001_initial'), (b'workflow', '0002_auto_20150922_1401'), (b'workflow', '0003_auto_20160520_1337'), (b'workflow', '0004_auto_20160802_1458'), (b'workflow', '0005_auto_20160802_1539'), (b'workflow', '0006_auto_20160802_1605'), (b'workflow', '0007_auto_20160803_0939')]

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
