# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0002_auto_20170523_1148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='baseentity',
            old_name='extFields',
            new_name='ext_fields',
        ),
        migrations.RenameField(
            model_name='speaker',
            old_name='extFields',
            new_name='ext_fields',
        ),
    ]
