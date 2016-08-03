# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0003_auto_20160520_1337'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflownode',
            name='attrs',
        ),
        migrations.RemoveField(
            model_name='workflownode',
            name='online',
        ),
        migrations.RemoveField(
            model_name='workflownode',
            name='roles',
        ),
    ]
