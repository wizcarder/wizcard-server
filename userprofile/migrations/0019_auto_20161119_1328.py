# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0018_auto_20161119_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2009, 12, 31, 18, 30, tzinfo=utc)),
        ),
    ]
