# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactcontainer',
            name='end',
        ),
        migrations.RemoveField(
            model_name='contactcontainer',
            name='start',
        ),
    ]
