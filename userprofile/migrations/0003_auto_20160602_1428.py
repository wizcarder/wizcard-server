# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_auto_20160310_1205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futureuser',
            name='phone',
            field=base.char_trunc.TruncatingCharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='device_id',
            field=base.char_trunc.TruncatingCharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='device_type',
            field=base.char_trunc.TruncatingCharField(default=b'ios', max_length=10, choices=[(b'ios', b'iPhone'), (b'android', b'Android')]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='userid',
            field=base.char_trunc.TruncatingCharField(max_length=100),
        ),
    ]
