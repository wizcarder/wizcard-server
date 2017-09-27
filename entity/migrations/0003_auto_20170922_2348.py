# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0004_auto_20170922_2348'),
        ('entity', '0002_auto_20170918_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaItem',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
                ('where', models.CharField(default=b'', max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.RemoveField(
            model_name='agenda',
            name='end',
        ),
        migrations.RemoveField(
            model_name='agenda',
            name='start',
        ),
        migrations.RemoveField(
            model_name='agenda',
            name='where',
        ),
        migrations.AddField(
            model_name='agendaitem',
            name='agenda',
            field=models.ForeignKey(related_name='items', to='entity.Agenda'),
        ),
    ]
