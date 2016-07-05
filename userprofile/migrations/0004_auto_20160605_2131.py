# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_auto_20160602_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='futureuser',
            name='email',
            field=base.emailField.EmailField(max_length=254, blank=True),
        ),
    ]
