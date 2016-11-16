# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dead_cards', '0004_deadcards_activated'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadcards',
            name='invited',
            field=models.BooleanField(default=False),
        ),
    ]
