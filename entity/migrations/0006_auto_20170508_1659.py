# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0005_auto_20170501_1446'),
    ]

    operations = [
        migrations.RenameField(
            model_name='speaker',
            old_name='ext_fields',
            new_name='extFields',
        ),
        migrations.AddField(
            model_name='baseentity',
            name='extFields',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
    ]
