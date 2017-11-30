# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0009_auto_20171201_0058'),
        ('entity', '0005_auto_20171122_1008'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sponsor',
            name='baseentitycomponent_ptr',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='created',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='description',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='email',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='ext_fields',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='name',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='vcard',
        ),
        migrations.RemoveField(
            model_name='sponsor',
            name='website',
        ),
        migrations.AddField(
            model_name='sponsor',
            name='baseentity_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=1, serialize=False, to='base_entity.BaseEntity'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='agendaitem',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='attendeeinvitee',
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
    ]
