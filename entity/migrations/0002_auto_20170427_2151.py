# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('speaker', '0001_initial'),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpeakerEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1000)),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='speakers',
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='event',
            field=models.ForeignKey(to='entity.Event'),
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='speaker',
            field=models.ForeignKey(to='speaker.Speaker'),
        ),
        migrations.AddField(
            model_name='event',
            name='speakers_tmp',
            field=models.ManyToManyField(related_name='events', through='entity.SpeakerEvent', to='speaker.Speaker'),
        ),
    ]
