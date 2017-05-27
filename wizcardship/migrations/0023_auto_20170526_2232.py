# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0022_remove_wizcard_emailtemplate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contactcontainer',
            old_name='f_bizCardImage',
            new_name='f_bizcard_image',
        ),
        migrations.RenameField(
            model_name='wizcard',
            old_name='extFields',
            new_name='ext_fields',
        ),
        migrations.RenameField(
            model_name='wizcard',
            old_name='smsurl',
            new_name='sms_url',
        ),
        migrations.RenameField(
            model_name='wizcard',
            old_name='thumbnailImage',
            new_name='thumbnail_image',
        ),
        migrations.RenameField(
            model_name='wizcard',
            old_name='videoThumbnailUrl',
            new_name='video_thumbnail_url',
        ),
        migrations.RenameField(
            model_name='wizcard',
            old_name='videoUrl',
            new_name='video_url',
        ),
    ]
