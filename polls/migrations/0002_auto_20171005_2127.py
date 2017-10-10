# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='is_published',
            field=models.BooleanField(default=False, verbose_name=b'is published'),
        ),
    ]
