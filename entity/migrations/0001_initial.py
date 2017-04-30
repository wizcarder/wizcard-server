# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_type', models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'BUS', b'Business'), (b'PRD', b'Product'), (b'TBL', b'Table')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('secure', models.BooleanField(default=False)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('is_activated', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=80, blank=True)),
                ('website', models.URLField()),
                ('description', models.CharField(max_length=1000)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
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
            ],
        ),
        migrations.CreateModel(
            name='UserEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='VirtualTable',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
                ('num_sitting', models.IntegerField(default=0, blank=True)),
                ('password', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.AddField(
            model_name='userentity',
            name='entity',
            field=models.ForeignKey(to='entity.BaseEntity'),
        ),
        migrations.AddField(
            model_name='userentity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
