# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('email_and_push_infra', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailandpush',
            name='event',
            field=models.ForeignKey(related_name='email_event', to='email_and_push_infra.EmailEvent'),
        ),
    ]
