# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizcard',
            name='email',
            field=models.EmailField(max_length=254, blank=True),
        ),
    ]