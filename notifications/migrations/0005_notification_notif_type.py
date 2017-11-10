# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_notification_delivery_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notif_type',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
