# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_global', models.BooleanField(default=False)),
                ('login', models.IntegerField(default=0, blank=True)),
                ('phone_check_req', models.IntegerField(default=0, blank=True)),
                ('phone_check_rsp', models.IntegerField(default=0, blank=True)),
                ('register', models.IntegerField(default=0, blank=True)),
                ('location_update', models.IntegerField(default=0, blank=True)),
                ('resync', models.IntegerField(default=0, blank=True)),
                ('contacts_upload', models.IntegerField(default=0, blank=True)),
                ('get_cards', models.IntegerField(default=0, blank=True)),
                ('ocr_self', models.IntegerField(default=0, blank=True)),
                ('ocr_dead', models.IntegerField(default=0, blank=True)),
                ('ocr_dead_edit', models.IntegerField(default=0, blank=True)),
                ('edit_card', models.IntegerField(default=0, blank=True)),
                ('edit_card_thumbnail', models.IntegerField(default=0, blank=True)),
                ('edit_card_video', models.IntegerField(default=0, blank=True)),
                ('edit_card_aboutme', models.IntegerField(default=0, blank=True)),
                ('edit_card_links', models.IntegerField(default=0, blank=True)),
                ('edit_card_notes', models.IntegerField(default=0, blank=True)),
                ('wizcard_accept', models.IntegerField(default=0, blank=True)),
                ('wizcard_decline', models.IntegerField(default=0, blank=True)),
                ('rolodex_edit', models.IntegerField(default=0, blank=True)),
                ('rolodex_delete', models.IntegerField(default=0, blank=True)),
                ('archived_cards', models.IntegerField(default=0, blank=True)),
                ('send_asset_xyz', models.IntegerField(default=0, blank=True)),
                ('send_asset_sms', models.IntegerField(default=0, blank=True)),
                ('send_asset_email', models.IntegerField(default=0, blank=True)),
                ('send_asset_wizcard', models.IntegerField(default=0)),
                ('send_asset_table', models.IntegerField(default=0, blank=True)),
                ('send_asset_fwd_wizcard', models.IntegerField(default=0, blank=True)),
                ('send_asset_invite_table', models.IntegerField(default=0, blank=True)),
                ('card_details', models.IntegerField(default=0, blank=True)),
                ('user_query', models.IntegerField(default=0, blank=True)),
                ('settings', models.IntegerField(default=0, blank=True)),
                ('email_template', models.IntegerField(default=0, blank=True)),
                ('get_recommendation', models.IntegerField(default=0, blank=True)),
                ('set_reco', models.IntegerField(default=0, blank=True)),
                ('get_common_connections', models.IntegerField(default=0, blank=True)),
                ('video_thumbnail', models.IntegerField(default=0, blank=True)),
                ('entity_create', models.IntegerField(default=0, blank=True)),
                ('entity_destroy', models.IntegerField(default=0, blank=True)),
                ('entity_edit', models.IntegerField(default=0, blank=True)),
                ('entity_join', models.IntegerField(default=0, blank=True)),
                ('entity_leave', models.IntegerField(default=0, blank=True)),
                ('entity_query', models.IntegerField(default=0, blank=True)),
                ('my_entities', models.IntegerField(default=0, blank=True)),
                ('entity_summary', models.IntegerField(default=0, blank=True)),
                ('entity_details', models.IntegerField(default=0, blank=True)),
                ('get_events', models.IntegerField(default=0, blank=True)),
                ('entities_engage', models.IntegerField(default=0, blank=True)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
