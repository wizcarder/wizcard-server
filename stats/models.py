from django.db import models
from django.contrib.auth.models import User
from wizserver import verbs
from django.db.models.signals import post_save
from userprofile.models import UserProfile
import pdb


# Create your models here.

class StatsMgr(models.Manager):
    # gets global stats row
    def get_global_stat(self):
        if not Stats.objects.filter(is_global=True).exists():
            # find admin user
            admin_user = UserProfile.objects.get_admin_user()

            # create and point to admin
            return Stats.objects.create(is_global=True, user=admin_user)
        else:
            return Stats.objects.get(is_global=True)

    def inc_login(self, user_stats, global_stats):
        global_stats.login += 1
        global_stats.save()

    def inc_phone_check_req(self, user_stats, global_stats):
        global_stats.phone_check_req += 1
        global_stats.save()

    def inc_phone_check_rsp(self, user_stats, global_stats):
        global_stats.phone_check_rsp += 1
        global_stats.save()

    def inc_register(self, user_stats, global_stats):
        user_stats.register += 1
        global_stats.register += 1

        user_stats.save()
        global_stats.save()

    def inc_location_update(self, user_stats, global_stats):
        user_stats.location_update += 1
        global_stats.location_update += 1

        user_stats.save()
        global_stats.save()

    def inc_resync(self, user_stats, global_stats):
        user_stats.resync += 1
        global_stats.resync += 1

        user_stats.save()
        global_stats.save()

    def inc_contacts_upload(self, user_stats, global_stats):
        user_stats.contacts_upload += 1
        global_stats.contacts_upload += 1

        user_stats.save()
        global_stats.save()

    def inc_get_cards(self, user_stats, global_stats):
        user_stats.get_cards += 1
        global_stats.get_cards += 1

        user_stats.save()
        global_stats.save()

    def inc_ocr_self(self, user_stats, global_stats):
        user_stats.ocr_self += 1
        global_stats.ocr_self += 1

        user_stats.save()
        global_stats.save()

    def inc_ocr_dead(self, user_stats, global_stats):
        user_stats.ocr_dead += 1
        global_stats.ocr_dead += 1

        user_stats.save()
        global_stats.save()

    def inc_ocr_dead_edit(self, user_stats, global_stats):
        user_stats.ocr_dead_edit += 1
        global_stats.ocr_dead_edit += 1

        user_stats.save()
        global_stats.save()

    def inc_edit_card(self, user_stats, global_stats):
        user_stats.edit_card += 1
        global_stats.edit_card += 1

        user_stats.save()

    def inc_edit_card_thumbnail(self, user_stats, global_stats):
        user_stats.edit_card_thumbnail += 1
        global_stats.edit_card_thumbnail += 1

        user_stats.save()
        global_stats.save()

    def inc_edit_card_video(self, user_stats, global_stats):
        user_stats.edit_card_video += 1
        global_stats.edit_card_video += 1

        user_stats.save()
        global_stats.save()

    def inc_edit_card_about_me(self, user_stats, global_stats):
        user_stats.edit_card_aboutme += 1
        global_stats.edit_card_aboutme += 1

        user_stats.save()
        global_stats.save()

    def inc_edit_card_links(self, user_stats, global_stats):
        user_stats.edit_card_links += 1
        global_stats.edit_card_links += 1

        user_stats.save()
        global_stats.save()

    def inc_edit_card_notes(self, user_stats, global_stats):
        user_stats.edit_card_notes += 1
        global_stats.edit_card_notes += 1

        user_stats.save()
        global_stats.save()

    def inc_wizcard_accept(self, user_stats, global_stats):
        user_stats.wizcard_accept += 1
        global_stats.wizcard_accept += 1

        user_stats.save()
        global_stats.save()


    def inc_wizcard_decline(self, user_stats, global_stats):
        user_stats.wizcard_decline += 1
        global_stats.wizcard_decline += 1

        user_stats.save()
        global_stats.save()

    def inc_rolodex_edit(self, user_stats, global_stats):
        global_stats.rolodex_edit += 1
        user_stats.rolodex_edit += 1

        user_stats.save()
        global_stats.save()

    def inc_rolodex_delete(self, user_stats, global_stats):
        global_stats.rolodex_delete += 1
        user_stats.rolodex_delete += 1

        user_stats.save()
        global_stats.save()

    def inc_archived_cards(self, user_stats, global_stats):
        global_stats.archived_cards += 1
        user_stats.archived_cards += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_xyz(self, user_stats, global_stats):
        user_stats.send_asset_xyz += 1
        global_stats.send_asset_xyz += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_sms(self, user_stats, global_stats):
        user_stats.send_asset_sms += 1
        global_stats.send_asset_sms += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_email(self, user_stats, global_stats):
        user_stats.send_asset_email += 1
        global_stats.send_asset_email += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_wizcard(self, user_stats, global_stats):
        user_stats.send_asset_wizcard += 1
        global_stats.send_asset_wizcard += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_table(self, user_stats, global_stats):
        user_stats.send_asset_table += 1
        global_stats.send_asset_table += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_fwd_wizcard(self, user_stats, global_stats):
        user_stats.send_asset_fwd_wizcard += 1
        global_stats.send_asset_fwd_wizcard += 1

        user_stats.save()
        global_stats.save()

    def inc_send_asset_invite_table(self, user_stats, global_stats):
        user_stats.send_asset_invite_table += 1
        global_stats.send_asset_invite_table += 1

        user_stats.save()
        global_stats.save()

    def inc_card_details(self, user_stats, global_stats):
        user_stats.card_details += 1
        global_stats.card_details += 1

        user_stats.save()
        global_stats.save()

    def inc_user_query(self, user_stats, global_stats):
        user_stats.user_query += 1
        global_stats.user_query += 1

        user_stats.save()
        global_stats.save()

    def inc_settings(self, user_stats, global_stats):
        user_stats.settings += 1
        global_stats.settings += 1

        user_stats.save()
        global_stats.save()

    def inc_email_template(self, user_stats, global_stats):
        user_stats.email_template += 1
        global_stats.email_template += 1

        user_stats.save()

    def inc_get_recommendation(self, user_stats, global_stats):
        user_stats.get_recommendation += 1
        global_stats.get_recommendation += 1

        user_stats.save()
        global_stats.save()

    def inc_set_reco(self, user_stats, global_stats):
        user_stats.set_reco += 1
        global_stats.set_reco += 1

        user_stats.save()
        global_stats.save()

    def inc_get_common_connections(self, user_stats, global_stats):
        user_stats.get_common_connections += 1
        global_stats.get_common_connections += 1

        user_stats.save()
        global_stats.save()

    def inc_video_thumbnail(self, user_stats, global_stats):
        user_stats.video_thumbnail += 1
        global_stats.video_thumbnail += 1

        user_stats.save()
        global_stats.save()

    def inc_events_get(self, user_stats, global_stats):
        user_stats.get_events += 1
        global_stats.get_events += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_create(self, user_stats, global_stats):
        user_stats.entity_create += 1
        global_stats.entity_create += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_destroy(self, user_stats, global_stats):
        user_stats.entity_destroy += 1
        global_stats.entity_destroy += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_edit(self, user_stats, global_stats):
        user_stats.entity_edit += 1
        global_stats.entity_edit += 1

        user_stats.save()
        global_stats.save()

    def inc_entities_like(self, user_stats, global_stats):
        user_stats.entities_like += 1
        global_stats.entities_like += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_join(self, user_stats, global_stats):
        user_stats.entity_join += 1
        global_stats.entity_join += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_leave(self, user_stats, global_stats):
        user_stats.entity_leave += 1
        global_stats.entity_leave += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_query(self, user_stats, global_stats):
        user_stats.entity_query += 1
        global_stats.entity_query += 1

        user_stats.save()
        global_stats.save()

    def inc_my_entities(self, user_stats, global_stats):
        user_stats.my_entities += 1
        global_stats.my_entities += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_summary(self, user_stats, global_stats):
        user_stats.entity_summary += 1
        global_stats.entity_summary += 1

        user_stats.save()
        global_stats.save()

    def inc_entity_details(self, user_stats, global_stats):
        user_stats.entity_details += 1
        global_stats.entity_details += 1

        user_stats.save()
        global_stats.save()


class Stats(models.Model):

    # lets use admin user to hold global stats
    user = models.OneToOneField(User, blank=True, null=True)
    is_global = models.BooleanField(default=False)

    # API stats
    login = models.IntegerField(blank=True, default=0)
    phone_check_req = models.IntegerField(blank=True, default=0)
    phone_check_rsp = models.IntegerField(blank=True, default=0)
    register = models.IntegerField(blank=True, default=0)
    location_update = models.IntegerField(blank=True, default=0)
    resync = models.IntegerField(blank=True, default=0)
    contacts_upload = models.IntegerField(blank=True, default=0)
    get_cards = models.IntegerField(blank=True, default=0)
    ocr_self = models.IntegerField(blank=True, default=0)
    ocr_dead = models.IntegerField(blank=True, default=0)
    ocr_dead_edit = models.IntegerField(blank=True, default=0)
    edit_card = models.IntegerField(blank=True, default=0)
    edit_card_thumbnail = models.IntegerField(blank=True, default=0)
    edit_card_video = models.IntegerField(blank=True, default=0)
    edit_card_aboutme = models.IntegerField(blank=True, default=0)
    edit_card_links = models.IntegerField(blank=True, default=0)
    edit_card_notes = models.IntegerField(blank=True, default=0)
    wizcard_accept = models.IntegerField(blank=True, default=0)
    wizcard_decline = models.IntegerField(blank=True, default=0)
    rolodex_edit = models.IntegerField(blank=True, default=0)
    rolodex_delete = models.IntegerField(blank=True, default=0)
    archived_cards = models.IntegerField(blank=True, default=0)
    send_asset_xyz = models.IntegerField(blank=True, default=0)
    send_asset_sms = models.IntegerField(blank=True, default=0)
    send_asset_email = models.IntegerField(blank=True, default=0)
    send_asset_wizcard = models.IntegerField(blank=False, default=0)
    send_asset_table = models.IntegerField(blank=True, default=0)
    send_asset_fwd_wizcard = models.IntegerField(blank=True, default=0)
    send_asset_invite_table = models.IntegerField(blank=True, default=0)
    card_details = models.IntegerField(blank=True, default=0)
    user_query = models.IntegerField(blank=True, default=0)
    settings = models.IntegerField(blank=True, default=0)
    email_template = models.IntegerField(blank=True, default=0)
    get_recommendation = models.IntegerField(blank=True, default=0)
    set_reco = models.IntegerField(blank=True, default=0)
    get_common_connections = models.IntegerField(blank=True, default=0)
    video_thumbnail = models.IntegerField(blank=True, default=0)
    entity_create = models.IntegerField(blank=True, default=0)
    entity_destroy = models.IntegerField(blank=True, default=0)
    entity_edit = models.IntegerField(blank=True, default=0)
    entity_join = models.IntegerField(blank=True, default=0)
    entity_leave = models.IntegerField(blank=True, default=0)
    entity_query = models.IntegerField(blank=True, default=0)
    my_entities = models.IntegerField(blank=True, default=0)
    entity_summary = models.IntegerField(blank=True, default=0)
    entity_details = models.IntegerField(blank=True, default=0)
    get_events = models.IntegerField(blank=True, default=0)
    entities_like = models.IntegerField(blank=True, default=0)

    objects = StatsMgr()


def create_user_stats(sender, instance, created, **kwargs):
    if created:
        user_stats = Stats(user=instance)
        if instance.profile.is_admin:
            user_stats.is_global = True
        user_stats.save()


post_save.connect(create_user_stats, sender=User)
