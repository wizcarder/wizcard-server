# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base_entity', '0002_auto_20170906_1747'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntityComponentsOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_creator', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='baseentitycomponentsuser',
            name='base_entity_component',
        ),
        migrations.RemoveField(
            model_name='baseentitycomponentsuser',
            name='user',
        ),
        migrations.RemoveField(
            model_name='baseentity',
            name='engagements',
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='engagements',
            field=models.OneToOneField(related_name='engagements_baseentitycomponent_related', null=True, to='base_entity.EntityEngagementStats'),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='baseentity',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='entity_type',
            field=models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'CMP', b'Campaign'), (b'TBL', b'Table'), (b'WZC', b'Wizcard'), (b'SPK', b'Speaker'), (b'SPN', b'Sponsor'), (b'COW', b'Coowner'), (b'ATT', b'Attendee'), (b'MED', b'Media'), (b'COW', b'Coowner'), (b'AGN', b'Agenda')]),
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentitycomponent_related', through='base_entity.BaseEntityComponentsOwner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='BaseEntityComponentsUser',
        ),
        migrations.AddField(
            model_name='baseentitycomponentsowner',
            name='base_entity_component',
            field=models.ForeignKey(to='base_entity.BaseEntityComponent'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsowner',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
