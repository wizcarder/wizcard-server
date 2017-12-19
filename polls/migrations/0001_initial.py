# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base_entity', '0011_remove_baseentity_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('description', models.CharField(max_length=100)),
                ('state', models.CharField(default=b'UNP', max_length=3, choices=[(b'UNP', b'unpublished'), (b'ACT', b'active'), (b'EXP', b'expired')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('base_entity.baseentitycomponent',),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_type', models.CharField(default=b'MCR', max_length=3, choices=[(b'TOF', b'TrueFalse'), (b'SCL', b'ScaleOf1toX'), (b'MCR', b'MultipleChoiceText'), (b'TXT', b'QuestionAnswerText')])),
                ('ui_type', models.CharField(default=b'SEL', max_length=3, choices=[(b'SEL', b'Select'), (b'SLD', b'GradedSlider'), (b'RAD', b'RadioButton'), (b'DRP', b'DropDown'), (b'TEX', b'TextArea'), (b'RTG', b'Rating')])),
                ('single_answer', models.BooleanField(default=True)),
                ('question', models.CharField(max_length=250, verbose_name=b'question')),
                ('extra_text', models.BooleanField(default=False)),
                ('poll', models.ForeignKey(related_name='questions', to='polls.Poll')),
                ('polymorphic_ctype', models.ForeignKey(related_name='polymorphic_polls.question_set+', editable=False, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'verbose_name': 'poll',
                'verbose_name_plural': 'polls',
            },
        ),
        migrations.CreateModel(
            name='QuestionChoicesBase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_text', models.BooleanField(default=False)),
                ('text', models.TextField()),
                ('has_user_value', models.BooleanField(default=False)),
                ('user_value', models.IntegerField(default=5, null=True, blank=True)),
                ('has_boolean_value', models.BooleanField(default=False)),
                ('boolean_value', models.BooleanField(default=True)),
                ('response_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionChoices1ToX',
            fields=[
                ('questionchoicesbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.QuestionChoicesBase')),
                ('low', models.IntegerField(default=0)),
                ('high', models.IntegerField(default=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.questionchoicesbase',),
        ),
        migrations.CreateModel(
            name='QuestionChoicesMultipleChoice',
            fields=[
                ('questionchoicesbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.QuestionChoicesBase')),
                ('question_key', models.CharField(max_length=1)),
                ('question_value', models.TextField()),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.questionchoicesbase',),
        ),
        migrations.CreateModel(
            name='QuestionChoicesText',
            fields=[
                ('questionchoicesbase_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='polls.QuestionChoicesBase')),
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
                ('true_key', models.CharField(default=b'Yes', max_length=10)),
                ('false_key', models.CharField(default=b'No', max_length=10)),
            ],
            options={
                'abstract': False,
            },
            bases=('polls.questionchoicesbase',),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='answer',
            field=models.ForeignKey(related_name='answers_userresponse_related', blank=True, to='polls.QuestionChoicesBase', null=True),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='poll',
            field=models.ForeignKey(to='polls.Poll'),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='question',
            field=models.ForeignKey(related_name='questions_userresponse_related', to='polls.Question'),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='questionchoicesbase',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_polls.questionchoicesbase_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='questionchoicesbase',
            name='question',
            field=models.ForeignKey(related_name='choices', to='polls.Question'),
        ),
    ]
