# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0012_auto_20161103_2320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='reco_generated_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 8, 6, 16, 18, 407941, tzinfo=utc)),
        ),
    ]
