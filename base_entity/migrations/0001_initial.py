# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntityComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_type', models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'BUS', b'Business'), (b'PRD', b'Product'), (b'TBL', b'Table'), (b'WZC', b'Wizcard'), (b'SPK', b'Speaker'), (b'SPN', b'Sponsor'), (b'COW', b'Coowner'), (b'ATT', b'Attendee'), (b'EXB', b'Exhibitor'), (b'MED', b'Media'), (b'COW', b'Coowner')])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BaseEntityComponentsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_creator', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='EntityEngagementStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('like_count', models.IntegerField(default=0)),
                ('views', models.IntegerField(default=0)),
                ('follows', models.IntegerField(default=0)),
                ('unfollows', models.IntegerField(default=0)),
                ('agg_like_level', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EntityUserStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('like_level', models.IntegerField(default=5)),
                ('following', models.BooleanField(default=False)),
                ('viewed', models.BooleanField(default=False)),
                ('stats', models.ForeignKey(to='base_entity.EntityEngagementStats')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BaseEntity',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('vcard', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('address', models.CharField(max_length=80, blank=True)),
                ('secure', models.BooleanField(default=False)),
                ('password', base.char_trunc.TruncatingCharField(max_length=40, null=True, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('is_activated', models.BooleanField(default=False)),
                ('num_users', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.AddField(
            model_name='entityengagementstats',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='base_entity.EntityUserStats'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='base_entity_component',
            field=models.ForeignKey(to='base_entity.BaseEntityComponent'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentitycomponent_related', through='base_entity.BaseEntityComponentsUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_base_entity.baseentitycomponent_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='userentity',
            name='entity',
            field=models.ForeignKey(to='base_entity.BaseEntity'),
        ),
    ]
