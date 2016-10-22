# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dead_cards', '0003_auto_20160605_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadcards',
            name='activated',
            field=models.BooleanField(default=False),
        ),
    ]
