# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import taggit.managers
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taganomy', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntityComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('stats', models.ForeignKey(to='entity.EntityEngagementStats')),
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
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntityComponent')),
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
                ('entity_type', models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'BUS', b'Business'), (b'PRD', b'Product'), (b'TBL', b'Table')])),
                ('secure', models.BooleanField(default=False)),
                ('password', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('is_activated', models.BooleanField(default=False)),
                ('num_users', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentitycomponent', models.Model),
        ),
        migrations.AddField(
            model_name='entityengagementstats',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='entity.EntityUserStats'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='base_entity_component',
            field=models.ForeignKey(to='entity.BaseEntityComponent'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentitycomponent_related', through='entity.BaseEntityComponentsUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_entity.baseentitycomponent_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='related_entities',
            field=models.ManyToManyField(related_name='related_entities_rel_+', to='entity.BaseEntityComponent', blank=True),
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.CreateModel(
            name='VirtualTable',
            fields=[
                ('baseentity_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.BaseEntity')),
            ],
            options={
                'abstract': False,
            },
            bases=('entity.baseentity',),
        ),
        migrations.AddField(
            model_name='userentity',
            name='entity',
            field=models.ForeignKey(to='entity.BaseEntity'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='category',
            field=models.ForeignKey(to='taganomy.Taganomy', blank=True),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='engagements',
            field=models.OneToOneField(related_name='engagements_baseentity_related', null=True, to='entity.EntityEngagementStats'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='users',
            field=models.ManyToManyField(related_name='users_baseentity_related', through='entity.UserEntity', to=settings.AUTH_USER_MODEL),
        ),
    ]
