# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0009_auto_20161102_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='dnd',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 3, 9, 16, 0, 796825, tzinfo=utc)),
        ),
    ]
