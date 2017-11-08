# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0009_auto_20171104_2120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
