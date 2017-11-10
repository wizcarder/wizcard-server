# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_notification_is_offline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='notification',
            old_name='is_offline',
            new_name='is_async',
        ),
    ]
