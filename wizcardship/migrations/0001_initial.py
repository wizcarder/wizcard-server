# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(max_length=40, blank=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('start', models.CharField(max_length=30, blank=True)),
                ('end', models.CharField(max_length=30, blank=True)),
                ('f_bizCardImage', base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'bizcards')),
                ('card_url', models.CharField(max_length=30, blank=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='UserBlocks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blocks', models.ManyToManyField(related_name='blocked_by_set', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='user_blocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user blocks',
                'verbose_name_plural': 'user blocks',
            },
        ),
        migrations.CreateModel(
            name='Wizcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=40, blank=True)),
                ('last_name', models.CharField(max_length=40, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('thumbnailImage', base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'thumbnails')),
                ('user', models.OneToOneField(related_name='wizcard', to=settings.AUTH_USER_MODEL)),
                ('wizconnections', models.ManyToManyField(related_name='wizconnections_rel_+', to='wizcardship.Wizcard', blank=True)),
            ],
            options={
                'verbose_name': 'wizcard',
                'verbose_name_plural': 'wizcards',
            },
        ),
        migrations.CreateModel(
            name='WizcardFlick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('a_created', models.CharField(max_length=40, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('lat', models.FloatField(default=None, null=True)),
                ('lng', models.FloatField(default=None, null=True)),
                ('flick_pickers', models.ManyToManyField(to='wizcardship.Wizcard')),
                ('wizcard', models.ForeignKey(related_name='flicked_cards', to='wizcardship.Wizcard')),
            ],
        ),
        migrations.CreateModel(
            name='WizConnectionRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.CharField(max_length=200, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('accepted', models.BooleanField(default=False)),
                ('from_wizcard', models.ForeignKey(related_name='invitations_from', to='wizcardship.Wizcard')),
                ('to_wizcard', models.ForeignKey(related_name='invitations_to', to='wizcardship.Wizcard')),
            ],
            options={
                'verbose_name': 'wizconnection request',
                'verbose_name_plural': 'wizconnection requests',
            },
        ),
        migrations.AddField(
            model_name='contactcontainer',
            name='wizcard',
            field=models.ForeignKey(related_name='contact_container', to='wizcardship.Wizcard'),
        ),
        migrations.AlterUniqueTogether(
            name='wizconnectionrequest',
            unique_together=set([('to_wizcard', 'from_wizcard')]),
        ),
    ]
