# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('title', base.char_trunc.TruncatingCharField(max_length=200, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='UserBlocks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blocks', models.ManyToManyField(related_name='blocked_by_set', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='user_blocks', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user blocks',
                'verbose_name_plural': 'user blocks',
            },
        ),
        migrations.CreateModel(
            name='WizcardBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vcard', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=20)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('sms_url', models.URLField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WizcardFlick',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('a_created', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('timeout', models.IntegerField(default=30)),
                ('lat', models.FloatField(default=None, null=True)),
                ('lng', models.FloatField(default=None, null=True)),
                ('expired', models.BooleanField(default=False)),
                ('reverse_geo_name', base.char_trunc.TruncatingCharField(default=None, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='WizConnectionRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cctx', picklefield.fields.PickledObjectField(editable=False, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Pending'), (2, b'Accepted'), (3, b'Declined'), (4, b'Deleted'), (5, b'Blocked')])),
            ],
            options={
                'verbose_name': 'wizconnection request',
                'verbose_name_plural': 'wizconnection requests',
            },
        ),
        migrations.CreateModel(
            name='DeadCard',
            fields=[
                ('wizcardbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wizcardship.WizcardBase')),
                ('invited', models.BooleanField(default=False)),
                ('activated', models.BooleanField(default=False)),
                ('cctx', picklefield.fields.PickledObjectField(editable=False, blank=True)),
                ('user', models.ForeignKey(related_name='dead_cards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('wizcardship.wizcardbase',),
        ),
        migrations.CreateModel(
            name='Wizcard',
            fields=[
                ('wizcardbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wizcardship.WizcardBase')),
                ('user', models.OneToOneField(related_name='wizcard', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'wizcard',
                'verbose_name_plural': 'wizcards',
            },
            bases=('wizcardship.wizcardbase',),
        ),
        migrations.AddField(
            model_name='wizcardbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_wizcardship.wizcardbase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='contactcontainer',
            name='wizcard',
            field=models.ForeignKey(related_name='contact_container', to='wizcardship.WizcardBase'),
        ),
        migrations.AddField(
            model_name='wizconnectionrequest',
            name='from_wizcard',
            field=models.ForeignKey(related_name='requests_from', to='wizcardship.Wizcard'),
        ),
        migrations.AddField(
            model_name='wizconnectionrequest',
            name='to_wizcard',
            field=models.ForeignKey(related_name='requests_to', to='wizcardship.Wizcard'),
        ),
        migrations.AddField(
            model_name='wizcardflick',
            name='flick_pickers',
            field=models.ManyToManyField(to='wizcardship.Wizcard'),
        ),
        migrations.AddField(
            model_name='wizcardflick',
            name='wizcard',
            field=models.ForeignKey(related_name='flicked_cards', to='wizcardship.Wizcard'),
        ),
        migrations.AddField(
            model_name='wizcard',
            name='wizconnections_to',
            field=models.ManyToManyField(related_name='wizconnections_from', through='wizcardship.WizConnectionRequest', to='wizcardship.Wizcard'),
        ),
        migrations.AlterUniqueTogether(
            name='wizconnectionrequest',
            unique_together=set([('to_wizcard', 'from_wizcard')]),
        ),
    ]
