# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-01 03:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('notifications', '0004_basenotification_notif_operation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basenotification',
            name='recipient',
        ),
        migrations.AddField(
            model_name='basenotification',
            name='recipient_content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notify_recipient', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='basenotification',
            name='recipient_object_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
