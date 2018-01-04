# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0012_auto_20171223_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeTemplate',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('company', base.char_trunc.TruncatingCharField(max_length=100, blank=True)),
                ('title', base.char_trunc.TruncatingCharField(max_length=200, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=2000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.CreateModel(
            name='ScannedEntity',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('company', base.char_trunc.TruncatingCharField(max_length=100, blank=True)),
                ('title', base.char_trunc.TruncatingCharField(max_length=200, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('event_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
    ]
