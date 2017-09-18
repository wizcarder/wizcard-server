# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0002_auto_20170912_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizcardbase',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='wizcardbase',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
