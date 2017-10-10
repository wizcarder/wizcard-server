# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0002_auto_20170906_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
