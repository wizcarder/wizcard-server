# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0009_auto_20180116_1218'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='ext_fields',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='website',
            field=models.URLField(blank=True),
        ),
    ]
