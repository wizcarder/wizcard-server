# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('wizcardship', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meishi',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(max_digits=20, decimal_places=15)),
                ('lng', models.DecimalField(max_digits=20, decimal_places=15)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('pairs', models.ManyToManyField(related_name='pairs_rel_+', to='meishi.Meishi', blank=True)),
                ('wizcard', models.ForeignKey(related_name='meishis', to='wizcardship.Wizcard')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
