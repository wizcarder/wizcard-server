# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0004_auto_20150521_0111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='futureuser',
            name='asset_type',
        ),
    ]
