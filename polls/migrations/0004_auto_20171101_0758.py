# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_auto_20171016_2119'),
    ]

    operations = [
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
