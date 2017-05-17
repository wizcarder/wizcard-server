# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_mgr', '0002_mediaobjects_media_videothumbnail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediaobjects',
            name='media_videothumbnail',
        ),
    ]
