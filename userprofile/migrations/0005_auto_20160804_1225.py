# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import base.char_trunc
from django.conf import settings
import base.emailField


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprofile', '0004_auto_20160605_2131'),
    ]

    operations = [
        migrations.CreateModel(
            name='AB_Candidate_Emails',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', base.emailField.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='AB_Candidate_Names',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', base.char_trunc.TruncatingCharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='AB_Candidate_Phones',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='AB_User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='AddressBook',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', base.char_trunc.TruncatingCharField(max_length=20, blank=True)),
                ('phone_finalized', models.BooleanField(default=False)),
                ('email', base.emailField.EmailField(max_length=254, blank=True)),
                ('email_finalized', models.BooleanField(default=False)),
                ('name', base.char_trunc.TruncatingCharField(max_length=40)),
                ('name_finalized', models.BooleanField(default=False)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='userprofile.AB_User')),
            ],
        ),
        migrations.AddField(
            model_name='ab_user',
            name='ab_entry',
            field=models.ForeignKey(to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_user',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ab_candidate_phones',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_phones', to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_candidate_names',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_names', to='userprofile.AddressBook'),
        ),
        migrations.AddField(
            model_name='ab_candidate_emails',
            name='ab_entry',
            field=models.ForeignKey(related_name='candidate_emails', to='userprofile.AddressBook'),
        ),
    ]
