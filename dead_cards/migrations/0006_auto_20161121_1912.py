# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dead_cards', '0005_deadcards_invited'),
    ]

    operations = [
        migrations.AddField(
            model_name='deadcards',
            name='cctx',
            field=picklefield.fields.PickledObjectField(editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='deadcards',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 21, 13, 42, 54, 925723, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
