# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0002_auto_20150628_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizconnectionrequest',
            name='cctx',
            field=picklefield.fields.PickledObjectField(editable=False, blank=True),
        ),
    ]
