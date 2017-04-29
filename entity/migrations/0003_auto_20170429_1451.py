# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20170429_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='designation',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='org',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
