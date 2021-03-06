# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-05 06:05
from __future__ import unicode_literals

import base.char_trunc
import base.emailField
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0010_auto_20180305_1135'),
        ('taganomy', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taganomy',
            name='category',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='editor',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='id',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='taganomy',
            name='updated',
        ),
        migrations.AddField(
            model_name='taganomy',
            name='baseentitycomponent_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='taganomy',
            name='email',
            field=base.emailField.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='taganomy',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='taganomy',
            name='name',
            field=base.char_trunc.TruncatingCharField(default=b'', max_length=50),
        ),
        migrations.AlterField(
            model_name='taganomy',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
