# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0006_auto_20160830_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addressbook',
            name='first_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='addressbook',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
    ]
