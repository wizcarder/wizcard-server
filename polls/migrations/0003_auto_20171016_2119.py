# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('polls', '0002_auto_20171005_2127'),
    ]

    operations = [
        migrations.AddField(
            model_name='userresponse',
            name='poll',
            field=models.ForeignKey(default=1, to='polls.Poll'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userresponse',
            name='user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userresponse',
            name='user_value',
            field=models.IntegerField(default=5, blank=True),
        ),
    ]
