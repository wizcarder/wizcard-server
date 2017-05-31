# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20170527_1019'),
    ]

    operations = [
        migrations.AddField(
            model_name='userentity',
            name='last_accessed',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 30, 15, 5, 14, 601915, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
