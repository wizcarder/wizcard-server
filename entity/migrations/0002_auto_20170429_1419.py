# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import taggit.managers
import base.emailField
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('last_name', base.char_trunc.TruncatingCharField(max_length=40, blank=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('vcard', models.TextField(blank=True)),
                ('org', models.CharField(default=None, max_length=100)),
                ('designation', models.CharField(default=None, max_length=100)),
                ('ext_fields', picklefield.fields.PickledObjectField(default={}, editable=False, blank=True)),
                ('description', models.TextField(default=b'Not Available')),
            ],
        ),
        migrations.AddField(
            model_name='baseentity',
            name='creator',
            field=models.ForeignKey(related_name='created_baseentity_related', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='baseentity',
            name='owners',
            field=models.ManyToManyField(related_name='owners_baseentity_related', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='polymorphic_ctype',
            field=models.ForeignKey(related_name='polymorphic_entity.baseentity_set+', editable=False, to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='baseentity',
            name='users',
            field=models.ManyToManyField(related_name='users_baseentity_related', through='entity.UserEntity', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='event',
            field=models.ForeignKey(default=1, to='entity.Event'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='event',
            name='speakers',
            field=models.ManyToManyField(related_name='events', through='entity.SpeakerEvent', to='entity.Speaker'),
        ),
        migrations.AddField(
            model_name='speakerevent',
            name='speaker',
            field=models.ForeignKey(default=1, to='entity.Speaker'),
            preserve_default=False,
        ),
    ]
