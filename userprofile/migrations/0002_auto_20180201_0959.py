# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='device_type',
            field=base.char_trunc.TruncatingCharField(max_length=10, choices=[(b'ios', b'iPhone'), (b'android', b'Android')]),
        ),
    ]
