# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.utils.timezone import utc
import datetime
from django.conf import settings
import base.emailField
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AB_Candidate_Emails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', base.emailField.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='AB_Candidate_Names',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', base.char_trunc.TruncatingCharField(max_length=40)),
                ('last_name', base.char_trunc.TruncatingCharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='AB_Candidate_Phones',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AB_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('phone_finalized', models.BooleanField(default=False)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('email_finalized', models.BooleanField(default=False)),
                ('first_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('last_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('first_name_finalized', models.BooleanField(default=False)),
                ('last_name_finalized', models.BooleanField(default=False)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='userprofile.AB_User')),
            ],
        ),
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
            name='FutureUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('inviter', models.ForeignKey(related_name='invitees', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('userid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('user_type', models.IntegerField(default=1)),
                ('activated', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WebExhibitorUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile', models.OneToOneField(related_name='exhibitor_user', to='userprofile.UserProfile')),
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
                ('profile', models.OneToOneField(related_name='organizer_user', to='userprofile.UserProfile')),
            ],
        ),
        migrations.CreateModel(
            name='WebOrganizerUserSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='weborganizeruser',
            name='settings',
            field=models.OneToOneField(related_name='organizer_user', to='userprofile.WebOrganizerUserSettings'),
        ),
        migrations.AddField(
            model_name='webexhibitoruser',
            name='settings',
            field=models.OneToOneField(related_name='exhibitor_user', to='userprofile.WebExhibitorUserSettings'),
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
        migrations.AddField(
            model_name='ab_user',
            name='ab_entry',
            field=models.ForeignKey(to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_user',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ab_candidate_phones',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_phones', to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_candidate_names',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_names', to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_candidate_emails',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_emails', to='userprofile.AddressBook'),
        ),
    ]
