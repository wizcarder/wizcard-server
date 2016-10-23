# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0007_auto_20160905_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 21, 16, 36, 16, 53831, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
