# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0003_auto_20170927_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactcontainer',
            name='company',
            field=base.char_trunc.TruncatingCharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcardbase',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
    ]
