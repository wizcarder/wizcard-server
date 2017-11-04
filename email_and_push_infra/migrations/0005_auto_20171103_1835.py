# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0004_auto_20171103_1825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 8, 13, 5, 6, 258461, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='emailandpush',
            name='event_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'RECUR'), (2, b'INSTANT'), (3, b'SCHEDULED')]),
        ),
    ]
