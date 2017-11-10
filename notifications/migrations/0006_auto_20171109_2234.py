# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0010_auto_20171104_2135'),
        ('notifications', '0005_notification_notif_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='email_push',
            field=models.ForeignKey(related_name='email_push_notif', blank=True, to='email_and_push_infra.EmailAndPush', null=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='delivery_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'email'), (2, b'alert'), (3, b'pushnotif')]),
        ),
    ]
