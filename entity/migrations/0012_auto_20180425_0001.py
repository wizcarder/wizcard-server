# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-25 05:01
from __future__ import unicode_literals

import base.char_trunc
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0011_auto_20180409_0625'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendeeinvitee',
            name='state',
        ),
        migrations.RemoveField(
            model_name='exhibitorinvitee',
            name='state',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='state',
        ),
        migrations.AddField(
            model_name='attendeeinvitee',
            name='phone',
            field=base.char_trunc.TruncatingCharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='exhibitorinvitee',
            name='invite_state',
            field=models.CharField(choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'REQ', b'Requested'), (b'ACC', b'Accepted'), (b'APA', b'App Accepted')], default=b'CRT', max_length=3),
        ),
    ]
