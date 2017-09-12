# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadcard',
            name='first_name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=30),
        ),
        migrations.AddField(
            model_name='deadcard',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=30),
        ),
    ]
