# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0004_stats_entities_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='entity_create',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_destroy',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_edit',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_query',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='entity_summary',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='stats',
            name='my_entities',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
