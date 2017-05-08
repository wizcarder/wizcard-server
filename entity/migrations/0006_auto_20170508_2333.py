# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0005_auto_20170501_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='EntityEngagementStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('like_count', models.IntegerField(default=0)),
                ('agg_like_level', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='EntityUserStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('like_level', models.IntegerField(default=5)),
                ('stats', models.ForeignKey(to='entity.EntityEngagementStats')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='entityengagementstats',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='entity.EntityUserStats'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='engagements',
            field=models.OneToOneField(related_name='engagements_baseentity_related', null=True, to='entity.EntityEngagementStats'),
        ),
    ]
