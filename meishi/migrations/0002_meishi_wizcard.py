# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
        ('meishi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meishi',
            name='wizcard',
            field=models.ForeignKey(related_name='meishis', to='wizcardship.Wizcard'),
        ),
    ]
