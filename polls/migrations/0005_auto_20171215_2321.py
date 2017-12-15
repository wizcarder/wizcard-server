# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0004_auto_20171128_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionChoicesMultipleChoice',
            fields=[
                ('questionchoicesbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.QuestionChoicesBase')),
                ('question_key', models.CharField(max_length=1)),
                ('question_value', models.TextField()),
                ('is_radio', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.questionchoicesbase',),
        ),
        migrations.CreateModel(
            name='QuestionChoicesTrueFalse',
            fields=[
                ('questionchoicesbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.QuestionChoicesBase')),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.questionchoicesbase',),
        ),
        migrations.RenameField(
            model_name='userresponse',
            old_name='has_extra_text',
            new_name='has_text',
        ),
        migrations.RenameField(
            model_name='userresponse',
            old_name='extra_text',
            new_name='text',
        ),
        migrations.RemoveField(
            model_name='poll',
            name='is_published',
        ),
        migrations.RemoveField(
            model_name='questionchoicestext',
            name='question_key',
        ),
        migrations.RemoveField(
            model_name='questionchoicestext',
            name='question_value',
        ),
        migrations.AddField(
            model_name='poll',
            name='state',
            field=models.CharField(default=b'UNP', max_length=3, choices=[(b'UNP', b'unpublished'), (b'ACT', b'active'), (b'EXP', b'expired')]),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='boolean_value',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='has_boolean_value',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(default=b'MCR', max_length=3, choices=[(b'TOF', b'TrueFalse'), (b'SCL', b'ScaleOf1toX'), (b'MCR', b'MultipleChoiceText'), (b'TXT', b'QuestionAnswerText')]),
        ),
        migrations.AlterField(
            model_name='question',
            name='ui_type',
            field=models.CharField(default=b'SEL', max_length=3, choices=[(b'SEL', b'Select'), (b'SLD', b'GradedSlider'), (b'RAD', b'RadioButton'), (b'DRP', b'DropDown'), (b'TEX', b'TextArea'), (b'RTG', b'Rating')]),
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
