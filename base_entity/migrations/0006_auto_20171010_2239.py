# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0005_auto_20170927_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentity',
            name='num_users',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='entity_type',
            field=models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'CMP', b'Campaign'), (b'TBL', b'Table'), (b'WZC', b'Wizcard'), (b'SPK', b'Speaker'), (b'SPN', b'Sponsor'), (b'COW', b'Coowner'), (b'ATI', b'AttendeeInvitee'), (b'EXI', b'ExhibitorInvitee'), (b'MED', b'Media'), (b'COW', b'Coowner'), (b'AGN', b'Agenda'), (b'AGI', b'AgendaItem'), (b'POL', b'Polls')]),
        ),
    ]
