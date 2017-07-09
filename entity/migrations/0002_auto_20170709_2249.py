# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taganomy', '0001_initial'),
        ('entity', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentitycomponentsbaseuser',
            name='base_user',
            field=models.ForeignKey(to='userprofile.BaseUser'),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentitycomponent_related', through='entity.BaseEntityComponentsBaseUser', to='userprofile.BaseUser'),
        ),
        migrations.AddField(
            model_name='baseentitycomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_entity.baseentitycomponent_set+', editable=False, to='contenttypes.ContentType', null=True),
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
