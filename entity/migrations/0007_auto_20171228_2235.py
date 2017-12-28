# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0006_auto_20171201_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendeeinvitee',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
        migrations.AddField(
            model_name='exhibitorinvitee',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
    ]
