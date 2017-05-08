# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_baseentity_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseentity',
            name='category',
            field=models.ForeignKey(default=10, to='taganomy.Taganomy'),
        ),
    ]
