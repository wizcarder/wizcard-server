# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-21 12:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scan', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgetemplate',
            name='created',
        ),
        migrations.RemoveField(
            model_name='badgetemplate',
            name='description',
        ),
        migrations.RemoveField(
            model_name='badgetemplate',
            name='email',
        ),
        migrations.RemoveField(
            model_name='badgetemplate',
            name='modified',
        ),
        migrations.RemoveField(
            model_name='badgetemplate',
            name='name',
        ),
        migrations.RemoveField(
            model_name='badgetemplate',
            name='website',
        ),
    ]