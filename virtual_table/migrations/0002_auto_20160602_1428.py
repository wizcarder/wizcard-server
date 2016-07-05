# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('virtual_table', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='virtualtable',
            name='a_created',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='virtualtable',
            name='password',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='virtualtable',
            name='tablename',
            field=base.char_trunc.TruncatingCharField(max_length=40),
        ),
    ]
