# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseNotification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actor_object_id', models.CharField(max_length=255)),
                ('verb', models.CharField(max_length=255)),
                ('target_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('action_object_object_id', models.CharField(max_length=255, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('public', models.BooleanField(default=True)),
                ('notif_type', models.PositiveIntegerField(default=0)),
                ('action_object_content_type', models.ForeignKey(related_name='notify_action_object', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor_content_type', models.ForeignKey(related_name='notify_actor', to='contenttypes.ContentType')),
                ('recipient', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('target_content_type', models.ForeignKey(related_name='notify_target', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={},
        ),
        migrations.RemoveField(
            model_name='notification',
            name='action_object_content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='action_object_object_id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor_content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='actor_object_id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='public',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='target_content_type',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='target_object_id',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='timestamp',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='verb',
        ),
        migrations.AddField(
            model_name='notification',
            name='basenotification_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=0,  serialize=False, to='notifications.BaseNotification'),
            preserve_default=False,
        ),
    ]
