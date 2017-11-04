# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_components', '0002_auto_20171028_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaentities',
            name='media_title',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
