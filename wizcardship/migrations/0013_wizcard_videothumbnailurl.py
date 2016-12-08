# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0012_auto_20161202_1535'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='videoThumbnailUrl',
            field=models.URLField(blank=True),
        ),
    ]
