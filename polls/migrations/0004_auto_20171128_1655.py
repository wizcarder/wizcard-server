# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20171016_2119'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userresponse',
            name='response_time',
            field=models.DateTimeField(default=django.utils.timezone.now, auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(default=b'MCT', max_length=3, choices=[(b'MCT', b'MultipleChoiceText'), (b'SCL', b'ScaleOf1toX'), (b'MCR', b'ChoiceAbcd'), (b'TOF', b'TrueFalse'), (b'QA', b'QuestionAnswer')]),
        ),
        migrations.AlterField(
            model_name='question',
            name='ui_type',
            field=models.CharField(default=b'SEL', max_length=3, choices=[(b'SEL', b'Select'), (b'SLD', b'GradedSlider'), (b'RAD', b'RadioButton'), (b'DRP', b'DropDown'), (b'TEX', b'TextArea')]),
        ),
    ]
