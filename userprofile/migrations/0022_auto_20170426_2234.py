# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0021_futureuser_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='user_type',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='device_type',
            field=base.char_trunc.TruncatingCharField(default=b'ios', max_length=10, choices=[(b'ios', b'iPhone'), (b'android', b'Android'), (b'Browser', b'Browser')]),
        ),
    ]
