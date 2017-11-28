# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
            name='id',
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
    ]
