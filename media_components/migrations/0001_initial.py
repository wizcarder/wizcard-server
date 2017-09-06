# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field
import base.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaEntities',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('media_type', models.CharField(default=b'IMG', max_length=3, choices=[(b'IMG', b'Image'), (b'VID', b'Video'), (b'DOC', b'Doc')])),
                ('media_sub_type', models.CharField(default=b'ROL', max_length=3, choices=[(b'BNR', b'Banner'), (b'LGO', b'Logo'), (b'SLG', b'Sponsor Logo'), (b'ROL', b'Rolling'), (b'THB', b'Thumbnail'), (b'FBZ', b'Business Card Front'), (b'DBZ', b'Dead Business Card'), (b'PVD', b'Profile Video'), (b'AGN', b'Agenda')])),
                ('upload_file', base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=base.mixins.get_s3_bucket, blank=True)),
                ('media_element', models.URLField(default=None, blank=True)),
                ('media_iframe', models.URLField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
    ]
