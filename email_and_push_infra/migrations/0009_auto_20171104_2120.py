# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0008_auto_20171104_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailandpush',
            name='delivery',
        ),
        migrations.AlterField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 9, 15, 50, 11, 501218, tzinfo=utc)),
        ),
    ]
