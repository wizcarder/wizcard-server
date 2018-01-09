# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0007_auto_20180104_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='is_sponsored',
            field=models.BooleanField(default=False),
        ),
    ]
