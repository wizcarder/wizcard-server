# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaObjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('media_type', models.CharField(default=b'IMG', max_length=3, choices=[(b'IMG', b'Image'), (b'VID', b'Video')])),
                ('media_sub_type', models.CharField(default=b'ROL', max_length=3, choices=[(b'BNR', b'Banner'), (b'LGO', b'Logo'), (b'SLG', b'Sponsor Logo'), (b'ROL', b'Rolling'), (b'THB', b'Thumbnail')])),
                ('media_element', models.URLField(default=None, blank=True)),
                ('media_iframe', models.URLField(blank=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
