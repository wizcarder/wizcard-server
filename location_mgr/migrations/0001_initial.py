# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationMgr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(default=None, null=True, max_digits=20, decimal_places=15)),
                ('lng', models.DecimalField(default=None, null=True, max_digits=20, decimal_places=15)),
                ('key', models.CharField(max_length=100, null=True)),
                ('tree_type', models.CharField(default=b'PTREE', max_length=10)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
