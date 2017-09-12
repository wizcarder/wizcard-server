# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailevent',
            name='event',
            field=models.PositiveSmallIntegerField(choices=[(1, b'NEWUSER'), (2, b'INVITED'), (3, b'SCANNED'), (4, b'RECOMMENDATION'), (5, b'MISSINGU'), (6, b'JOINUS'), (7, b'DIGEST'), (8, b'INVITE_EXHIBITOR'), (9, b'INVITE_ATTENDEE')]),
        ),
    ]
