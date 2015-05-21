# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0002_auto_20150518_0623'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcardflick',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]
