# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taganomy', '__first__'),
        ('entity', '0003_auto_20170429_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='category',
            field=models.ForeignKey(default=10, to='taganomy.Taganomy'),
        ),
    ]
