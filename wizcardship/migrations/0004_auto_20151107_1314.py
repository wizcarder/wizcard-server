# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0003_auto_20150628_1631'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='wizcard',
            name='wizconnections',
        ),
        migrations.RemoveField(
            model_name='wizconnectionrequest',
            name='accepted',
        ),
        migrations.AddField(
            model_name='wizcard',
            name='wizconnections_to',
            field=models.ManyToManyField(related_name='wizconnections_from', through='wizcardship.WizConnectionRequest', to='wizcardship.Wizcard'),
        ),
        migrations.AddField(
            model_name='wizconnectionrequest',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Pending'), (2, b'Accepted'), (4, b'Blocked')]),
        ),
        migrations.AlterField(
            model_name='wizconnectionrequest',
            name='from_wizcard',
            field=models.ForeignKey(related_name='requests_from', to='wizcardship.Wizcard'),
        ),
        migrations.AlterField(
            model_name='wizconnectionrequest',
            name='to_wizcard',
            field=models.ForeignKey(related_name='requests_to', to='wizcardship.Wizcard'),
        ),
    ]
