# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deadcard',
            name='cctx',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
    ]
