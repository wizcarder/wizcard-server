# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-10 03:39
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('base_entity', '0009_auto_20171201_0058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='baseentity',
            name='category',
        ),
        migrations.RemoveField(
            model_name='baseentity',
            name='expired',
        ),
        migrations.RemoveField(
            model_name='baseentity',
            name='is_activated',
        ),
        migrations.RemoveField(
            model_name='baseentity',
            name='tags',
        ),
        migrations.AddField(
            model_name='baseentity',
            name='venue',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='entity_state',
            field=models.CharField(choices=[(b'CRT', b'Created'), (b'PUB', b'Published'), (b'EXP', b'Expired'), (b'DEL', b'Deleted')], default=b'CRT', max_length=3),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='userentity',
            name='state',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='entity_type',
            field=models.CharField(choices=[(b'EVT', b'Event'), (b'CMP', b'Campaign'), (b'TBL', b'Table'), (b'WZC', b'Wizcard'), (b'SPK', b'Speaker'), (b'SPN', b'Sponsor'), (b'COW', b'Coowner'), (b'ATI', b'AttendeeInvitee'), (b'EXI', b'ExhibitorInvitee'), (b'MED', b'Media'), (b'COW', b'Coowner'), (b'AGN', b'Agenda'), (b'AGI', b'AgendaItem'), (b'POL', b'Polls'), (b'BDG', b'Badges'), (b'SCN', b'Scans'), (b'CAT', b'Category')], default=b'EVT', max_length=3),
        ),
    ]