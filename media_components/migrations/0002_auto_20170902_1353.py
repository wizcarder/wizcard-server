# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('media_components', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediaentities',
            name='media_sub_type',
            field=models.CharField(default=b'ROL', max_length=3, choices=[(b'BNR', b'Banner'), (b'LGO', b'Logo'), (b'SLG', b'Sponsor Logo'), (b'ROL', b'Rolling'), (b'THB', b'Thumbnail'), (b'FBZ', b'Business Card Front'), (b'DBZ', b'Dead Business Card'), (b'PVD', b'Profile Video'), (b'AGN', b'Agenda')]),
        ),
        migrations.AlterField(
            model_name='mediaentities',
            name='media_type',
            field=models.CharField(default=b'IMG', max_length=3, choices=[(b'IMG', b'Image'), (b'VID', b'Video'), (b'DOC', b'Doc')]),
        ),
    ]
