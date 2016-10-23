# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('recommendation', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommenderMeta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modelscore', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
                ('recomodel', models.IntegerField(choices=[(0, b'AB_RECO'), (1, b'WIZCONNECTIONS_RECO')])),
            ],
        ),
        migrations.RemoveField(
            model_name='recommendation',
            name='recomodel',
        ),
        migrations.RemoveField(
            model_name='recommendation',
            name='score',
        ),
        migrations.AddField(
            model_name='userrecommendation',
            name='lastaction_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 21, 16, 36, 7, 891762, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userrecommendation',
            name='score',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='userrecommendation',
            name='reco',
            field=models.ForeignKey(related_name='user_recos', to='recommendation.Recommendation'),
        ),
        migrations.AddField(
            model_name='recommendermeta',
            name='userrecommend',
            field=models.ForeignKey(related_name='reco_meta', to='recommendation.UserRecommendation'),
        ),
    ]
