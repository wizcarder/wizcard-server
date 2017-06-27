# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import base.char_trunc
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0022_auto_20170426_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('do_sync', models.BooleanField(default=False)),
                ('device_id', base.char_trunc.TruncatingCharField(max_length=100)),
                ('reg_token', models.CharField(max_length=200, db_index=True)),
                ('device_type', base.char_trunc.TruncatingCharField(default=b'unknown', max_length=10, choices=[(b'ios', b'iPhone'), (b'android', b'Android')])),
                ('reco_generated_at', models.DateTimeField(default=datetime.datetime(2009, 12, 31, 18, 30, tzinfo=utc))),
                ('reco_ready', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='AppUserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_profile_private', models.BooleanField(default=False)),
                ('is_wifi_data', models.BooleanField(default=False)),
                ('is_visible', models.BooleanField(default=True)),
                ('dnd', models.BooleanField(default=False)),
                ('block_unsolicited', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WebExhibitorUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebExhibitorUserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebOrganizerUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='WebOrganizerUserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='block_unsolicited',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='device_id',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='device_type',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='dnd',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='do_sync',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='future_user',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_profile_private',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_visible',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_wifi_data',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='reco_generated_at',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='reco_ready',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='reg_token',
        ),
        migrations.AddField(
            model_name='weborganizeruser',
            name='profile',
            field=models.OneToOneField(related_name='organizer_user', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='weborganizeruser',
            name='settings',
            field=models.OneToOneField(related_name='organizer_settings', to='userprofile.WebOrganizerUserSettings'),
        ),
        migrations.AddField(
            model_name='webexhibitoruser',
            name='profile',
            field=models.OneToOneField(related_name='exhibitor_user', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='webexhibitoruser',
            name='settings',
            field=models.OneToOneField(related_name='exhibitor_settings', to='userprofile.WebOrganizerUserSettings'),
        ),
        migrations.AddField(
            model_name='appuser',
            name='profile',
            field=models.OneToOneField(related_name='app_user', to='userprofile.UserProfile'),
        ),
        migrations.AddField(
            model_name='appuser',
            name='settings',
            field=models.OneToOneField(related_name='app_user', to='userprofile.AppUserSettings'),
        ),
    ]
