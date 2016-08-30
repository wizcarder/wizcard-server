# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0005_auto_20160804_1225'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ab_candidate_names',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='addressbook',
            old_name='name',
            new_name='first_name',
        ),
        migrations.RenameField(
            model_name='addressbook',
            old_name='name_finalized',
            new_name='first_name_finalized',
        ),
        migrations.AddField(
            model_name='ab_candidate_names',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(default='', max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='addressbook',
            name='last_name',
            field=base.char_trunc.TruncatingCharField(default='', max_length=40),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='addressbook',
            name='last_name_finalized',
            field=models.BooleanField(default=False),
        ),
    ]
