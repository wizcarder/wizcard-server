# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0009_auto_20171201_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='venue',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
