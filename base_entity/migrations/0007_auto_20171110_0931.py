# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0006_auto_20171010_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentity',
            name='description',
            field=models.CharField(max_length=2000, blank=True),
        ),
    ]
