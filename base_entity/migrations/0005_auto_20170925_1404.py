# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0004_auto_20170922_2348'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='address',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='baseentitycomponentsowner',
            unique_together=set([('base_entity_component', 'owner')]),
        ),
    ]
