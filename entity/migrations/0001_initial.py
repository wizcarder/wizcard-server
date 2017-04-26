# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import taggit.managers
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('speaker', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_type', models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'BUS', b'Business'), (b'PRD', b'Product'), (b'TBL', b'Table')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('secure', models.BooleanField(default=False)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('is_activated', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=80, blank=True)),
                ('website', models.URLField()),
                ('description', models.CharField(max_length=1000)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
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
                ('speakers', models.ManyToManyField(related_name='events', to='speaker.Speaker')),
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
                ('num_sitting', models.IntegerField(default=0, blank=True)),
                ('password', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
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
            model_name='userentity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='creator',
            field=models.ForeignKey(related_name='created_baseentity_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentity_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_entity.baseentity_set+', editable=False, to='contenttypes.ContentType', null=True),
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
