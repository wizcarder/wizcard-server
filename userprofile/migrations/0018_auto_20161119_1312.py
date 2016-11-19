# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0017_auto_20161115_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 19, 4, 42, 28, 183869, tzinfo=utc)),
        ),
    ]
