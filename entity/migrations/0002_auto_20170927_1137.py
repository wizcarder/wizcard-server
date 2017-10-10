# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0005_auto_20170927_1137'),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaItem',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', base.char_trunc.TruncatingCharField(default=b'', max_length=50)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('website', models.URLField(blank=True)),
                ('description', models.CharField(max_length=1000, blank=True)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(auto_now_add=True)),
                ('where', models.CharField(default=b'', max_length=100)),
                ('agenda', models.ForeignKey(related_name='items', to='entity.Agenda')),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent', models.Model),
        ),
        migrations.RenameModel(
            old_name='Business',
            new_name='Campaign',
        ),
        migrations.RemoveField(
            model_name='product',
            name='baseentity_ptr',
        ),
        migrations.AlterField(
            model_name='attendeeinvitee',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='attendeeinvitee',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='coowners',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='coowners',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='exhibitorinvitee',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='exhibitorinvitee',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='sponsor',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
