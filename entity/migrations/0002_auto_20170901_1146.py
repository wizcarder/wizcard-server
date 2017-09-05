# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendeeinvitee',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='coowners',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='exhibitorinvitee',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
    ]
