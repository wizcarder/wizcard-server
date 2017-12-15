# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0010_baseentity_venue'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseentity',
            name='category',
        ),
    ]
