# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FutureUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('asset_type', models.CharField(max_length=20)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('inviter', models.ForeignKey(related_name='invitees', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activated', models.BooleanField(default=False)),
                ('userid', models.CharField(max_length=100)),
                ('future_user', models.BooleanField(default=False)),
                ('do_sync', models.BooleanField(default=False)),
                ('is_profile_private', models.BooleanField(default=False)),
                ('is_wifi_data', models.BooleanField(default=False)),
                ('is_visible', models.BooleanField(default=True)),
                ('block_unsolicited', models.BooleanField(default=False)),
                ('device_type', models.CharField(default=b'ios', max_length=10, choices=[(b'ios', b'iPhone'), (b'android', b'Android')])),
                ('device_id', models.CharField(max_length=100)),
                ('reg_token', models.CharField(max_length=100)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
