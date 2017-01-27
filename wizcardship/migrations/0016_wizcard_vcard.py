# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0015_remove_wizcard_thumbnailvideo'),
    ]

    operations = [
        migrations.AddField(
            model_name='wizcard',
            name='vcard',
            field=models.TextField(blank=True),
        ),
    ]
