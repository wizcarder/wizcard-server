# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-05 06:05
from __future__ import unicode_literals

import base.char_trunc
import base.emailField
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0010_auto_20180305_1135'),
        ('entity', '0006_auto_20171201_0058'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='agendaitem',
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('base_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.RenameField(
            model_name='agendaitem',
            old_name='agenda',
            new_name='agenda_key',
        ),
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
            model_name='agenda',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='description',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='agenda',
            name='email',
            field=base.emailField.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='agenda',
            name='ext_fields',
            field=picklefield.fields.PickledObjectField(blank=True, default={}, editable=False),
        ),
        migrations.AddField(
            model_name='agenda',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='agenda',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AddField(
            model_name='agenda',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='agendaitem',
            name='baseentity_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base_entity.BaseEntity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendeeinvitee',
            name='company',
            field=base.char_trunc.TruncatingCharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='attendeeinvitee',
            name='state',
            field=models.CharField(choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')], default=b'CRT', max_length=3),
        ),
        migrations.AddField(
            model_name='attendeeinvitee',
            name='title',
            field=base.char_trunc.TruncatingCharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='campaign',
            name='is_sponsored',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exhibitorinvitee',
            name='state',
            field=models.CharField(choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')], default=b'CRT', max_length=3),
        ),
        migrations.AddField(
            model_name='sponsor',
            name='state',
            field=models.CharField(choices=[(b'CRT', b'Created'), (b'INV', b'Invited'), (b'ACC', b'Accepted')], default=b'CRT', max_length=3),
        ),
    ]
