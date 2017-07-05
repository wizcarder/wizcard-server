# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='speaker',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='speaker',
            name='last_name',
        ),
        migrations.AddField(
            model_name='speaker',
            name='address',
            field=models.CharField(max_length=80, blank=True),
        ),
        migrations.AddField(
            model_name='speaker',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 5, 15, 25, 58, 96607, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='speaker',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 5, 15, 26, 4, 184512, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='speaker',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='description',
            field=models.CharField(max_length=1000, blank=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='ext_fields',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='name',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='description',
            field=models.CharField(max_length=1000, blank=True),
        ),
    ]
