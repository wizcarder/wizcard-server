# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0011_wizcard_smsurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizcard',
            name='extFields',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
    ]
