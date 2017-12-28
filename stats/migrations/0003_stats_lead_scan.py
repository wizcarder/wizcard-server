# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_stats_poll_response'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='lead_scan',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
