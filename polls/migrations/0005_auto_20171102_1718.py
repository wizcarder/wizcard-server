# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20171101_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 2, 11, 48, 25, 632765, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userresponse',
            name='response_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 2, 11, 48, 36, 583423, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
