# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0002_auto_20170709_2249'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseEntityComponentsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_creator', models.BooleanField(default=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='baseentitycomponentsbaseuser',
            name='base_entity',
        ),
        migrations.RemoveField(
            model_name='baseentitycomponentsbaseuser',
            name='base_user',
        ),
        migrations.AlterField(
            model_name='baseentitycomponent',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentitycomponent_related', through='entity.BaseEntityComponentsUser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='BaseEntityComponentsBaseUser',
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='base_entity',
            field=models.ForeignKey(to='entity.BaseEntityComponent'),
        ),
        migrations.AddField(
            model_name='baseentitycomponentsuser',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
