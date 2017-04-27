# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20170427_2151'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='speakers_tmp',
            new_name='speakers',
        ),
    ]
