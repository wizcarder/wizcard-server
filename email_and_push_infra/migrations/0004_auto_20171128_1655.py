# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0003_auto_20171128_1655'),
        ('notifications', '0002_auto_20171128_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailandpush',
            name='basenotification_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.BaseNotification'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='delivery_mode',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'email'), (2, b'alert'), (3, b'pushnotif'), (4, b'sms')]),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='delivery_period',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'RECUR'), (2, b'INSTANT'), (3, b'SCHEDULED')]),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='readed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='status',
            field=models.PositiveSmallIntegerField(default=1, choices=[(0, b'success'), (-1, b'failed'), (1, b'new')]),
        ),
        migrations.DeleteModel(
            name='EmailEvent',
        ),
    ]
