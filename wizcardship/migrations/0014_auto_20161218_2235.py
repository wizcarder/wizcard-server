# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0013_wizcard_videothumbnailurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='thumbnailVideo',
            field=base.custom_field.WizcardQueuedFileField(default=b'wizcard-image-bucket-stage/thumbnails/no-video-uploaded.gif', storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'thumbnails'),
        ),
        migrations.AlterField(
            model_name='wizcard',
            name='thumbnailImage',
            field=base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'thumbnails', blank=True),
        ),
    ]
