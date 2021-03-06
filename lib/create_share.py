#!/usr/bin/env python
from __future__ import absolute_import

from celery import shared_task
from django.utils import timezone
from media_components.models import MediaEntities
from django.template import Context
from lib.ses import Email
import vobject
from wizcardship.models import Wizcard
from entity.models import Event
import pdb

now = timezone.now


def create_vcard(wizcard):
    v = vobject.vCard()
    v.add('n')
    v.n.value = vobject.vcard.Name(family=wizcard.user.last_name, given=wizcard.user.first_name)
    v.add('fn')
    v.fn.value = wizcard.get_name()
    v.add('email')
    v.email.value = wizcard.email
    v.add('tel')
    v.tel.value = wizcard.phone
    v.tel.type_param = 'cell'
    v.add('org')
    v.org.value = [wizcard.get_latest_company()]
    v.add('title')
    v.title.value = wizcard.get_latest_title()
    tnurl = wizcard.get_thumbnail_url()

    for url in tnurl:
        v.add('photo')
        v.photo.value = url
        v.photo.type_param = 'jpeg'

    return v.serialize()


@shared_task
def send_wizcard(from_wizcard, to, email_details, half_card=False):

    extfields = from_wizcard.get_ext_fields
    html = email_details['template']
    subject = email_details['subject']

    if not extfields:
        extfields = {}

    sender_image = from_wizcard.get_thumbnail_url()
    if sender_image:
        extfields['sender_image'] = sender_image

    extfields['sender_name'] = from_wizcard.get_name()
    extfields['sender_org'] = from_wizcard.get_latest_company()
    extfields['sender_title'] = from_wizcard.get_latest_title()
    extfields['sender_phone'] = from_wizcard.phone
    extfields['sender_email'] = from_wizcard.email
    sender_video = from_wizcard.get_video_url
    if sender_video:
        extfields['sender_video'] = sender_video

    subject = subject % extfields['sender_name']
    if half_card:
        extfields['sender_phone'] = '***********'
        extfields['sender_email'] = '*****@*****.***'

    email = Email(to=to, subject=subject)
    ctx = extfields
    email.html(html, ctx)
    attach_data = None
    vcard = from_wizcard.get_vcard

    if not half_card and vcard:
        attach_name = "%s-%s.vcf" % (from_wizcard.user.first_name, from_wizcard.user.last_name)
        attach_data = {'data': from_wizcard.get_vcard, 'mime': 'text/vcard', 'name': attach_name}

    email.send(attach=attach_data)
    return 0


@shared_task
def send_event(event, to, email_details):
    email_dict = dict()
    html = email_details['template']
    email_dict['event_name'] = event.name
    event_media = event.get_media_filter(type=MediaEntities.TYPE_IMAGE, sub_type=MediaEntities.SUB_TYPE_BANNER)
    if event_media:
        event_media = event_media[0]

    # AA: Review. Fix this so we don't forget before production
    email_dict['banner'] = 'http://PlaceholderImage.com'

    if event_media:
        email_dict['banner'] = event_media.media_element

    #ctx = Context(email_dict)
    ctx = email_dict

    email = Email(to=to, subject=email_details['subject'])
    email.html(html, ctx)
    email.send()
#    email.send(from_addr=emaildetails['from_addr'])


def mass_email(to, id):

    email = Email(to=to, subject="Aren\'t paper business cards such a pain??")

    ctx = Context({'id': id})
    email.html('email_marketing2.html', ctx)
    email.send()
