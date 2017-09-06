# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('base_entity', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taganomy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseentity',
            name='category',
            field=models.ForeignKey(to='taganomy.Taganomy', blank=True),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='engagements',
            field=models.OneToOneField(related_name='engagements_baseentity_related', null=True, to='base_entity.EntityEngagementStats'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='users',
            field=models.ManyToManyField(related_name='users_baseentity_related', through='base_entity.UserEntity', to=settings.AUTH_USER_MODEL),
        ),
    ]
