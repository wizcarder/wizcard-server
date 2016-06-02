# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('dead_cards', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deadcards',
            name='company',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='deadcards',
            name='first_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='deadcards',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='deadcards',
            name='phone',
            field=base.char_trunc.TruncatingCharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='deadcards',
            name='title',
            field=base.char_trunc.TruncatingCharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='deadcards',
            name='web',
            field=base.char_trunc.TruncatingCharField(max_length=200, blank=True),
        ),
    ]
