# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0003_auto_20170918_1407'),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Business',
            new_name='Campaign',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.AddField(
            model_name='agenda',
            name='end',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 18, 8, 37, 25, 376527, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agenda',
            name='start',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 18, 8, 37, 28, 318420, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='agenda',
            name='where',
            field=models.CharField(default=b'', max_length=100),
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
    ]
