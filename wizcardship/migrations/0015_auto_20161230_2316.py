# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0014_auto_20161218_2235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wizcard',
            name='thumbnailVideo',
            field=base.custom_field.WizcardQueuedFileField(default=b'wizcard-image-bucket-prod/thumbnails/no-video-uploaded.gif', storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'thumbnails'),
        ),
    ]
