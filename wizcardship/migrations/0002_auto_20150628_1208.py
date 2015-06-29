# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wizconnectionrequest',
            name='message',
        ),
        migrations.AddField(
            model_name='wizconnectionrequest',
            name='cctx',
            field=picklefield.fields.PickledObjectField(default=None, editable=False),
        ),
    ]
