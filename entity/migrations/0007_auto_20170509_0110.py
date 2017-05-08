# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0006_auto_20170508_2333'),
    ]

    operations = [
        migrations.RenameField(
            model_name='speaker',
            old_name='ext_fields',
            new_name='extFields',
        ),
    ]
