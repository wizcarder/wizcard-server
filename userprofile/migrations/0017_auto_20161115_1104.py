# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0016_auto_20161115_1101'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='reco_ready',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 15, 2, 34, 0, 627632, tzinfo=utc)),
        ),
    ]
