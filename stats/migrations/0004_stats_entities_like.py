# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0003_auto_20170426_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='entities_like',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
