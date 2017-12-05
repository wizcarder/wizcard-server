# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0008_auto_20171122_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentity',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
    ]
