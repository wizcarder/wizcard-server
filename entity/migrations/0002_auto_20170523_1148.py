# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='virtualtable',
            name='num_sitting',
        ),
        migrations.RemoveField(
            model_name='virtualtable',
            name='password',
        ),
        migrations.AddField(
            model_name='baseentity',
            name='num_users',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='password',
            field=base.char_trunc.TruncatingCharField(max_length=40, blank=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='extFields',
            field=picklefield.fields.PickledObjectField(default={b'key': b'value'}, editable=False, blank=True),
        ),
    ]
