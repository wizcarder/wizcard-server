# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_auto_20160603_2134'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='description',
        ),
    ]
