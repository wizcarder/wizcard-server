# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0002_auto_20150527_1803'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcardflick',
            name='reverse_geo_name',
            field=models.CharField(default=None, max_length=100),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='wizcard',
            name='email',
            field=models.EmailField(max_length=75, blank=True),
            preserve_default=True,
        ),
    ]
