# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('email_and_push_infra', '0002_auto_20170219_1325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailandpush',
            name='wizcard',
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='sender_content_type',
            field=models.ForeignKey(related_name='email_and_push', default=15, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='sender_object_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='emailevent',
            name='event',
            field=models.PositiveSmallIntegerField(choices=[(1, b'NEWUSER'), (2, b'INVITED'), (3, b'SCANNED'), (4, b'RECOMMENDATION'), (5, b'MISSINGU'), (6, b'JOINUS'), (7, b'DIGEST'), (8, b'INVITE_EXHIBITOR')]),
        ),
    ]
