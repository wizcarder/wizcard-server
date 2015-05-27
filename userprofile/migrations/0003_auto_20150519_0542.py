# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_auto_20150517_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='reg_token',
            field=models.CharField(max_length=100, db_index=True),
        ),
    ]
