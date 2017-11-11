# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20171014_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agendaitem',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
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
        migrations.AlterField(
            model_name='speaker',
            name='company',
            field=base.char_trunc.TruncatingCharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
    ]
