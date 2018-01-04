# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('base_entity', '0012_auto_20171223_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseentity',
            name='tags',
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='entity_type',
            field=models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'CMP', b'Campaign'), (b'TBL', b'Table'), (b'WZC', b'Wizcard'), (b'SPK', b'Speaker'), (b'SPN', b'Sponsor'), (b'COW', b'Coowner'), (b'ATI', b'AttendeeInvitee'), (b'EXI', b'ExhibitorInvitee'), (b'MED', b'Media'), (b'COW', b'Coowner'), (b'AGN', b'Agenda'), (b'AGI', b'AgendaItem'), (b'POL', b'Polls'), (b'BDG', b'Badges'), (b'SCN', b'Scans'), (b'CAT', b'Category')]),
        ),
    ]
