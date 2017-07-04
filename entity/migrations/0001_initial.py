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
            name='BaseEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entity_type', models.CharField(default=b'EVT', max_length=3, choices=[(b'EVT', b'Event'), (b'BUS', b'Business'), (b'PRD', b'Product'), (b'TBL', b'Table')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('secure', models.BooleanField(default=False)),
                ('password', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('is_activated', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=80, blank=True)),
                ('website', models.URLField()),
                ('description', models.CharField(max_length=1000)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={b'key': b'value'}, editable=False, blank=True)),
                ('num_users', models.IntegerField(default=1)),
            ],
            options={
                'abstract': False,
            },
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
            name='EventComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(default=b'Not Available', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SpeakerEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='SponsorEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserEntity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_accessed', models.DateTimeField(auto_now=True)),
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
            name='Speaker',
            fields=[
                ('eventcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.EventComponent')),
                ('first_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('last_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('vcard', models.TextField(blank=True)),
                ('org', models.CharField(max_length=100, blank=True)),
                ('designation', models.CharField(max_length=100, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('description', models.TextField(blank=True)),
            ],
            bases=('entity.eventcomponent',),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('eventcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.EventComponent')),
                ('name', base.char_trunc.TruncatingCharField(max_length=50, blank=True)),
            ],
            bases=('entity.eventcomponent',),
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
            model_name='userentity',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='entityengagementstats',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='entity.EntityUserStats'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='category',
            field=models.ForeignKey(to='taganomy.Taganomy', blank=True),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='creator',
            field=models.ForeignKey(related_name='created_baseentity_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='engagements',
            field=models.OneToOneField(related_name='engagements_baseentity_related', null=True, to='entity.EntityEngagementStats'),
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
        migrations.AddField(
            model_name='sponsorevent',
            name='campaign',
            field=models.ForeignKey(blank=True, to='entity.Product', null=True),
        ),
        migrations.AddField(
            model_name='sponsorevent',
            name='event',
            field=models.ForeignKey(to='entity.Event'),
        ),
        migrations.AddField(
            model_name='sponsorevent',
            name='sponsor',
            field=models.ForeignKey(to='entity.Sponsor'),
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='event',
            field=models.ForeignKey(to='entity.Event'),
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='speaker',
            field=models.ForeignKey(to='entity.Speaker'),
        ),
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(related_name='events', through='entity.SpeakerEvent', to='entity.Speaker'),
        ),
        migrations.AddField(
            model_name='event',
            name='sponsors',
            field=models.ManyToManyField(related_name='events', through='entity.SponsorEvent', to='entity.Sponsor'),
        ),
    ]
