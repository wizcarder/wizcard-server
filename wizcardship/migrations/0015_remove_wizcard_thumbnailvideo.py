# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0014_auto_20161218_2235'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wizcard',
            name='thumbnailVideo',
        ),
    ]
