# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('readed', models.BooleanField(default=False)),
                ('acted_upon', models.BooleanField(default=True)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(max_length=255)),
                ('target_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('action_object_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=True)),
                ('action_object_content_type', models.ForeignKey(related_name='notify_action_object', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor_content_type', models.ForeignKey(related_name='notify_actor', to='contenttypes.ContentType')),
                ('recipient', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('target_content_type', models.ForeignKey(related_name='notify_target', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
    ]
