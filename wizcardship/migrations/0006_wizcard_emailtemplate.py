# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0005_auto_20160310_1205'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='emailTemplate',
            field=base.custom_field.WizcardQueuedFileField(default='', storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'invites'),
            preserve_default=False,
        ),
    ]
