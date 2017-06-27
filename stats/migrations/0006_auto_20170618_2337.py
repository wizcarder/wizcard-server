# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0005_auto_20170523_1148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stats',
            old_name='entities_like',
            new_name='entities_engage',
        ),
    ]
