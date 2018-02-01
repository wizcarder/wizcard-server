# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20171128_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncNotification',
            fields=[
                ('basenotification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.BaseNotification')),
                ('delivery_period', models.PositiveSmallIntegerField(default=2, choices=[(1, b'RECUR'), (2, b'INSTANT'), (3, b'SCHEDULED')])),
                ('last_tried', models.DateTimeField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('status', models.PositiveSmallIntegerField(default=1, choices=[(0, b'success'), (-1, b'failed'), (1, b'new')])),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('end_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('notifcation_text', models.CharField(default=b'', max_length=100)),
            ],
            bases=('notifications.basenotification',),
        ),
        migrations.CreateModel(
            name='SyncNotification',
            fields=[
                ('basenotification_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='notifications.BaseNotification')),
                ('acted_upon', models.BooleanField(default=True)),
            ],
            bases=('notifications.basenotification',),
        ),
        migrations.RemoveField(
            model_name='notification',
            name='basenotification_ptr',
        ),
        migrations.AddField(
            model_name='basenotification',
            name='delivery_mode',
            field=models.PositiveSmallIntegerField(default=2, choices=[(1, b'email'), (2, b'alert')]),
        ),
        migrations.AddField(
            model_name='basenotification',
            name='readed',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
