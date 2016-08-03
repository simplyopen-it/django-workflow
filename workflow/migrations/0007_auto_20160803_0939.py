# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0006_auto_20160802_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflow',
            name='head',
        ),
        migrations.RemoveField(
            model_name='workflownode',
            name='incomings',
        ),
        migrations.RenameField(
            model_name='workflow',
            old_name='head_new',
            new_name='head',
        ),
        migrations.RenameField(
            model_name='workflownode',
            old_name='outcomings_new',
            new_name='outcomings',
        ),
    ]
