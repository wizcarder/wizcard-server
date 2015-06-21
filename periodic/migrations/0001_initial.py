# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('location_mgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Periodic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timeout_value', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('timer_type', models.IntegerField(default=1)),
                ('location', models.ForeignKey(related_name='timer', to='location_mgr.LocationMgr')),
            ],
        ),
    ]
