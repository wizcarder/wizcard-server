# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('email_and_push_infra', '0002_auto_20170912_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailandpush',
            old_name='last_sent',
            new_name='last_tried',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='event',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='sender_content_type',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='sender_object_id',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='target_content_type',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='target_object_id',
        ),
        migrations.RemoveField(
            model_name='emailandpush',
            name='to',
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 3, 10, 26, 0, 843327, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='delivery',
            field=models.PositiveSmallIntegerField(default=1, choices=[(1, b'email'), (2, b'pushnotif'), (3, b'sms')]),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 8, 10, 25, 31, 3032, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='event_type',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'BUFFERED'), (2, b'INSTANT')]),
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
