# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('taganomy', '0002_auto_20180104_0846'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taganomy',
            name='category',
        ),
        migrations.AddField(
            model_name='taganomy',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='taganomy',
            name='email',
            field=base.emailField.EmailField(max_length=254, blank=True),
        ),
        migrations.AddField(
            model_name='taganomy',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='taganomy',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
    ]
