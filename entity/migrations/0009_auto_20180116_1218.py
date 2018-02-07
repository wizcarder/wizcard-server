# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0008_campaign_is_sponsored'),
    ]

    operations = [
        migrations.AddField(
            model_name='agenda',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='email',
            field=base.emailField.EmailField(max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
    ]
