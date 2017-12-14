# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20171128_1655'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='poll',
            name='is_published',
        ),
        migrations.AddField(
            model_name='poll',
            name='state',
            field=models.CharField(default=b'UNP', max_length=3, choices=[(b'UNP', b'unpublished'), (b'ACT', b'active'), (b'EXP', b'expired')]),
        ),
        migrations.AlterField(
            model_name='userresponse',
            name='answer',
            field=models.ForeignKey(related_name='answers_userresponse_related', to='polls.QuestionChoicesBase'),
        ),
        migrations.AlterField(
            model_name='userresponse',
            name='question',
            field=models.ForeignKey(related_name='questions_userresponse_related', to='polls.Question'),
        ),
    ]
