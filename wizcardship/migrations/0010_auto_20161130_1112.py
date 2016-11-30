# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0009_auto_20160912_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='extFields',
            field=picklefield.fields.PickledObjectField(editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='wizcard',
            name='videoUrl',
            field=models.URLField(blank=True),
        ),
    ]
