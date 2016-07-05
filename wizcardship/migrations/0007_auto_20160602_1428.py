# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0006_wizcard_emailtemplate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactcontainer',
            name='company',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='contactcontainer',
            name='end',
            field=base.char_trunc.TruncatingCharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='contactcontainer',
            name='phone',
            field=base.char_trunc.TruncatingCharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='contactcontainer',
            name='start',
            field=base.char_trunc.TruncatingCharField(max_length=30, blank=True),
        ),
        migrations.AlterField(
            model_name='contactcontainer',
            name='title',
            field=base.char_trunc.TruncatingCharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcard',
            name='first_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcard',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcard',
            name='phone',
            field=base.char_trunc.TruncatingCharField(max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcardflick',
            name='a_created',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='wizcardflick',
            name='reverse_geo_name',
            field=base.char_trunc.TruncatingCharField(default=None, max_length=100),
        ),
    ]
