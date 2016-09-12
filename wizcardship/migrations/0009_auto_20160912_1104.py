# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0008_auto_20160605_2131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizconnectionrequest',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Pending'), (2, b'Accepted'), (3, b'Declined'), (4, b'Deleted'), (5, b'Blocked')]),
        ),
    ]
