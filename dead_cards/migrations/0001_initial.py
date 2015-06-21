# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.custom_storage
import base.custom_field
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeadCards',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=40, blank=True)),
                ('last_name', models.CharField(max_length=40, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('company', models.CharField(max_length=40, blank=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('web', models.CharField(max_length=200, blank=True)),
                ('f_bizCardImage', base.custom_field.WizcardQueuedFileField(storage=base.custom_storage.WizcardQueuedS3BotoStorage(delayed=False), upload_to=b'deadcards')),
                ('user', models.ForeignKey(related_name='dead_cards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
