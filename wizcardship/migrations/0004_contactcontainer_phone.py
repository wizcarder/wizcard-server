# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0003_wizcardflick_expired'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactcontainer',
            name='phone',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
