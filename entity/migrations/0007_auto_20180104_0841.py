# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0013_auto_20180104_0841'),
        ('entity', '0006_auto_20171201_0058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agendaitem',
            name='baseentitycomponent_ptr',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='created',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='description',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='email',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='ext_fields',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='name',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='website',
        ),
        migrations.RemoveField(
            model_name='agendaitem',
            name='where',
        ),
        migrations.AddField(
            model_name='agendaitem',
            name='baseentity_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendeeinvitee',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
        migrations.AddField(
            model_name='exhibitorinvitee',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='state',
            field=models.CharField(default=b'CRT', max_length=3, choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')]),
        ),
    ]
