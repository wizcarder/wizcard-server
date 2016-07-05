# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_acted_upon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='acted_upon',
            field=models.BooleanField(default=True),
        ),
    ]
