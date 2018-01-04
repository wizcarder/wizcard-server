# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0013_auto_20180104_0841'),
        ('taganomy', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taganomy',
            name='created',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='id',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='updated',
        ),
        migrations.AddField(
            model_name='taganomy',
            name='baseentitycomponent_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent'),
            preserve_default=False,
        ),
    ]
