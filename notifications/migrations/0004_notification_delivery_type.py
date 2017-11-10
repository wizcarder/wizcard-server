# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20171104_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='delivery_type',
            field=models.PositiveSmallIntegerField(default=4, choices=[(1, b'email'), (2, b'pushnotif'), ((3,), b'sms'), (4, b'alert')]),
        ),
    ]
