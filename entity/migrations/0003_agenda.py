# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0004_auto_20170902_1353'),
        ('entity', '0002_auto_20170901_1146'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent',),
        ),
    ]
