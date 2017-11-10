# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_components', '0003_mediaentities_media_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediaentities',
            name='media_title',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
