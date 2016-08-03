# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django_extensions.db.fields.json import JSONField


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0004_auto_20160802_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow',
            name='head_new',
            field=models.SlugField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='workflownode',
            name='outcomings_new',
            field=JSONField(default=list),
        ),


    ]
