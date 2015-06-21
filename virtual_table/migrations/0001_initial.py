# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VirtualTable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tablename', models.CharField(max_length=40)),
                ('numSitting', models.IntegerField(default=0, blank=True)),
                ('secureTable', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=40, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('a_created', models.CharField(max_length=40, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('expired', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(related_name='tables', to=settings.AUTH_USER_MODEL)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='virtual_table.Membership')),
            ],
        ),
        migrations.AddField(
            model_name='membership',
            name='table',
            field=models.ForeignKey(to='virtual_table.VirtualTable'),
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
