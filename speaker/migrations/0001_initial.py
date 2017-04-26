# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100)),
                ('is_activated', models.BooleanField(default=False)),
                ('social_profile', models.URLField(default=None)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('thumbnail', models.URLField(default=None)),
                ('org', models.CharField(default=None, max_length=100)),
                ('designation', models.CharField(default=None, max_length=100)),
                ('description', models.TextField(default=b'Not Available')),
                ('user', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
