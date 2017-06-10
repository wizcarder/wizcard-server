# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc


class Migration(migrations.Migration):

    dependencies = [
        ('entity', '0004_userentity_last_accessed'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventComponent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('caption', models.CharField(default=b'Not Available', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='SponsorEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign', models.ForeignKey(blank=True, to='entity.Product', null=True)),
                ('event', models.ForeignKey(to='entity.Event')),
            ],
        ),
        migrations.RemoveField(
            model_name='speaker',
            name='id',
        ),
        migrations.AlterField(
            model_name='speaker',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('eventcomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='entity.EventComponent')),
                ('name', base.char_trunc.TruncatingCharField(max_length=50, blank=True)),
            ],
            bases=('entity.eventcomponent',),
        ),
        migrations.AddField(
            model_name='speaker',
            name='eventcomponent_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=None, serialize=False, to='entity.EventComponent'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='sponsorevent',
            name='sponsor',
            field=models.ForeignKey(to='entity.Sponsor'),
        ),
        migrations.AddField(
            model_name='event',
            name='sponsors',
            field=models.ManyToManyField(related_name='events', through='entity.SponsorEvent', to='entity.Sponsor'),
        ),
    ]
