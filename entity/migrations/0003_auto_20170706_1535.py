# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0002_auto_20170705_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventcomponent',
            name='component_type',
            field=models.CharField(default=b'SPK', max_length=3, choices=[(b'SPK', b'Speaker'), (b'SPN', b'Sponsor')]),
        ),
        migrations.AddField(
            model_name='eventcomponent',
            name='creator',
            field=models.ForeignKey(related_name='created_eventcomponent_related', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eventcomponent',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_entity.eventcomponent_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
    ]
