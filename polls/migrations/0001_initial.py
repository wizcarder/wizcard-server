# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base_entity', '0006_auto_20171010_2239'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('baseentitycomponent_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='base_entity.BaseEntityComponent')),
                ('description', models.CharField(max_length=100)),
                ('is_published', models.BooleanField(default=False, verbose_name=b'is published')),
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
                ('question_type', models.CharField(default=b'MCT', max_length=3, choices=[(b'MCT', b'MultipleChoiceText'), (b'SCL', b'ScaleOf1toX'), (b'MCR', b'ChoiceAbcd'), (b'TOF', b'TrueFalse')])),
                ('ui_type', models.CharField(default=b'SEL', max_length=3, choices=[(b'SEL', b'Select'), (b'SLD', b'GradedSlider'), (b'RAD', b'RadioButton'), (b'DRP', b'DropDown')])),
                ('single_answer', models.BooleanField(default=True)),
                ('question', models.CharField(max_length=250, verbose_name=b'question')),
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
                ('extra_text', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('has_extra_text', models.BooleanField(default=False)),
                ('extra_text', models.TextField()),
                ('has_user_value', models.BooleanField(default=False)),
                ('user_value', models.IntegerField(blank=True)),
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
            name='QuestionChoicesText',
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
        migrations.AddField(
            model_name='userresponse',
            name='answer',
            field=models.ForeignKey(to='polls.QuestionChoicesBase'),
        ),
        migrations.AddField(
            model_name='userresponse',
            name='question',
            field=models.ForeignKey(to='polls.Question'),
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
