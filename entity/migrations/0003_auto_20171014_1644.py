# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0002_auto_20170927_1137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coowners',
            name='created',
        ),
        migrations.RemoveField(
            model_name='coowners',
            name='email',
        ),
        migrations.RemoveField(
            model_name='coowners',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='coowners',
            name='name',
        ),
        migrations.AddField(
            model_name='coowners',
            name='user',
            field=models.OneToOneField(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
