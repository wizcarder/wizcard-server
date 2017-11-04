# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0005_auto_20171103_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 8, 16, 36, 39, 588119, tzinfo=utc)),
        ),
    ]
