# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_auto_20170509_1245'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='extFields',
            field=picklefield.fields.PickledObjectField(default={}, editable=False, blank=True),
        ),
    ]
