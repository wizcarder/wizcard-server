# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
        ('entity_components', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(related_name='events', through='entity_components.SpeakerEvent', to='entity_components.Speaker'),
        ),
        migrations.AddField(
            model_name='event',
            name='sponsors',
            field=models.ManyToManyField(related_name='events', through='entity_components.SponsorEvent', to='entity_components.Sponsor'),
        ),
    ]
