# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeInvitee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('caption', models.CharField(default=b'Not Available', max_length=50)),
                ('vcard', models.TextField(blank=True)),
                ('org', models.CharField(max_length=100, blank=True)),
                ('designation', models.CharField(max_length=100, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SpeakerEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1000)),
                ('event', models.ForeignKey(to='entity.Event')),
                ('speaker', models.ForeignKey(to='entity_components.Speaker')),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('caption', models.CharField(default=b'Not Available', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SponsorEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign', models.ForeignKey(blank=True, to='entity.Product', null=True)),
                ('event', models.ForeignKey(to='entity.Event')),
                ('sponsor', models.ForeignKey(to='entity_components.Sponsor')),
            ],
        ),
        migrations.CreateModel(
            name='TeamOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
        ),
    ]
