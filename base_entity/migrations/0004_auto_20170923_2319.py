# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0003_baseentity_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentity',
            name='address',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
