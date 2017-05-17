# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_auto_20161221_1629'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='entity_details',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_join',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_leave',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='get_events',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
