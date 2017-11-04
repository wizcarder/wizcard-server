# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0007_auto_20171104_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 9, 7, 54, 19, 370604, tzinfo=utc)),
        ),
    ]
