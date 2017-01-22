# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0020_userprofile_is_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='futureuser',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 1, 22, 11, 11, 41, 958315, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
