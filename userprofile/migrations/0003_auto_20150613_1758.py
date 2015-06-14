# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0002_auto_20150527_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futureuser',
            name='email',
            field=models.EmailField(max_length=75, blank=True),
            preserve_default=True,
        ),
    ]
