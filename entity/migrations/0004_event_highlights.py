# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0003_auto_20171014_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='highlights',
            field=picklefield.fields.PickledObjectField(editable=False, blank=True),
        ),
    ]
