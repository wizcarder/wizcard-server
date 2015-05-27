# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0005_remove_futureuser_asset_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futureuser',
            name='email',
            field=models.EmailField(max_length=75, blank=True),
            preserve_default=True,
        ),
    ]
