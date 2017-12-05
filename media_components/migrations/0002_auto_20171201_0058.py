# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_components', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediaentities',
            name='media_title',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='mediaentities',
            name='media_element',
            field=models.URLField(default=None, max_length=300, blank=True),
        ),
        migrations.AlterField(
            model_name='mediaentities',
            name='media_type',
            field=models.CharField(default=b'IMG', max_length=3, choices=[(b'IMG', b'Image'), (b'VID', b'Video'), (b'AUD', b'Audio'), (b'DOC', b'Doc')]),
        ),
    ]
