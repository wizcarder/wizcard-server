# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtual_table', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualtable',
            name='expired',
            field=models.BooleanField(default=False),
        ),
    ]
