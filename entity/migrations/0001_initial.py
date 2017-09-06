# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent',),
        ),
        migrations.CreateModel(
            name='AttendeeInvitee',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentity',),
        ),
        migrations.CreateModel(
            name='CoOwners',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntity')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentity',),
        ),
        migrations.CreateModel(
            name='ExhibitorInvitee',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentity',),
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('vcard', models.TextField(blank=True)),
                ('company', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('title', base.char_trunc.TruncatingCharField(max_length=200, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('vcard', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('caption', models.CharField(default=b'Not Available', max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='VirtualTable',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentity',),
        ),
    ]
