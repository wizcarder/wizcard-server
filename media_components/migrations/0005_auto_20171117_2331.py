# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_components', '0004_auto_20171109_0015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediaentities',
            name='media_element',
            field=models.URLField(default=None, max_length=300, blank=True),
        ),
    ]
