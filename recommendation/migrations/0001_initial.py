# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reco_object_id', models.PositiveIntegerField()),
                ('reco_content_type', models.ForeignKey(related_name='reco', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='RecommenderMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modelscore', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
                ('recomodel', models.IntegerField(choices=[(0, b'AB_RECO'), (1, b'WIZCONNECTIONS_RECO')])),
            ],
        ),
        migrations.CreateModel(
            name='UserRecommendation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('useraction', models.PositiveSmallIntegerField(default=3, choices=[(0, b'VIEWED'), (1, b'ACTED'), (2, b'DISMISSED'), (3, b'NEW')])),
                ('score', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
                ('lastaction_time', models.DateTimeField(auto_now=True)),
                ('reco', models.ForeignKey(related_name='user_recos', to='recommendation.Recommendation')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='recommendermeta',
            name='userrecommend',
            field=models.ForeignKey(related_name='reco_meta', to='recommendation.UserRecommendation'),
        ),
        migrations.AddField(
            model_name='recommendation',
            name='recommendation_for',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='recommendation.UserRecommendation'),
        ),
    ]
