# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dead_cards', '0006_auto_20161121_1912'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deadcards',
            old_name='f_bizCardImage',
            new_name='f_bizcard_image',
        ),
    ]
