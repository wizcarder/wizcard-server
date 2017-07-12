# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.custom_storage
import base.mixins
import picklefield.fields
import base.custom_field
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendeeInvitee',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='CoOwners',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='ExhibitorInvitee',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='MediaEntities',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('media_type', models.CharField(default=b'IMG', max_length=3, choices=[(b'IMG', b'Image'), (b'VID', b'Video')])),
                ('media_sub_type', models.CharField(default=b'ROL', max_length=3, choices=[(b'BNR', b'Banner'), (b'LGO', b'Logo'), (b'SLG', b'Sponsor Logo'), (b'ROL', b'Rolling'), (b'THB', b'Thumbnail'), (b'FBZ', b'Business Card Front'), (b'DBZ', b'Dead Business Card'), (b'PVD', b'Profile Video')])),
                ('upload_file', base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=base.mixins.get_s3_bucket, blank=True)),
                ('media_element', models.URLField(default=None, blank=True)),
                ('media_iframe', models.URLField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('vcard', models.TextField(blank=True)),
                ('company', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('title', base.char_trunc.TruncatingCharField(max_length=200, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
                ('vcard', models.TextField(blank=True)),
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
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
    ]
