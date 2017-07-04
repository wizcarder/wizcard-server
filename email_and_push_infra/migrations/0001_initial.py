# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailAndPush',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sender_object_id', models.PositiveIntegerField()),
                ('to', base.emailField.EmailField(max_length=254, blank=True)),
                ('target_object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('last_sent', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EmailEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.PositiveSmallIntegerField(choices=[(1, b'NEWUSER'), (2, b'INVITED'), (3, b'SCANNED'), (4, b'RECOMMENDATION'), (5, b'MISSINGU'), (6, b'JOINUS'), (7, b'DIGEST'), (8, b'INVITE_EXHIBITOR')])),
                ('event_type', models.PositiveSmallIntegerField(default=2, choices=[(1, b'BUFFERED'), (2, b'INSTANT')])),
            ],
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='event',
            field=models.ForeignKey(related_name='email_event', to='email_and_push_infra.EmailEvent'),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='sender_content_type',
            field=models.ForeignKey(related_name='email_and_push', default=15, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='emailandpush',
            name='target_content_type',
            field=models.ForeignKey(related_name='email_target', blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
