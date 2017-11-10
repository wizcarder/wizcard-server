# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_event_highlights'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendaitem',
            name='end',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='agendaitem',
            name='start',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
