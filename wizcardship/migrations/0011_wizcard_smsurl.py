# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0010_auto_20161130_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='smsurl',
            field=models.URLField(blank=True),
        ),
    ]
