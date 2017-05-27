#!/usr/bin/env python
from __future__ import absolute_import
import sys
import StringIO, hashlib
from celery import shared_task
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage as storage
from django.template import Template,Context
from django.utils.encoding import smart_str, smart_unicode
from wizcardship.models import WizcardManager, Wizcard
from wizcard import settings
from PIL import Image,ImageFont, ImageDraw, ImageOps
from lib.ses import Email
import vobject
import requests
import pdb
now = timezone.now


@shared_task
def create_template(wizcard):

    resource = storage.open(settings.EMAIL_TEMPLATE)

    image_url = wizcard.get_thumbnail_url()
    if image_url:
        response = requests.get(image_url)
        thumbimg = Image.open(StringIO.StringIO(response.content))
        wid, hei = thumbimg.size
    #    if  wid != 80:
        thumbimg = thumbimg.resize((90, 90), Image.ANTIALIAS)
        size = (90, 90)
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        thumbimg = ImageOps.fit(thumbimg, mask.size, centering=(0.5, 0.5))
        thumbimg.putalpha(mask)

#    data = {"name" : wizcard.first_name + " " + wizcard.last_name, "company": wizcard.get_latest_company(), "title" : wizcard.get_latest_title(), "email" : wizcard.email, "phone" : wizcard.phone}
    data = {"name" : smart_str(wizcard.first_name) + " " + smart_str(wizcard.last_name), "company": smart_str(wizcard.get_latest_company()), "title" : smart_str(wizcard.get_latest_title()), "email" : smart_str(wizcard.email), "phone" : smart_str(wizcard.phone)}
    data["invite_name"] = data["name"]

#    position = {'email': '490,462', 'title': '380,388', 'phone': '198,464', 'name':'378,315', 'company' : '381, 371'}
#    position = {'email': '490,462', 'title': '380,395', 'phone': '198,464', 'name':'378,315', 'company' : '381, 371', 'invite_name':'300,600'}
    position = {'email': '296,275', 'title': '254,245', 'phone': '143,275', 'name':'250,182', 'company' : '252, 216', 'invite_name':'207,370'}
    fonts = {'email': ImageFont.truetype('Roboto-Regular.ttf',12), 
             'title': ImageFont.truetype('Roboto-Regular.ttf', 16),
             'phone': ImageFont.truetype('Roboto-Regular.ttf', 12), 
             'name': ImageFont.truetype('Roboto-Regular.ttf',22),
             'invite_name':ImageFont.truetype('Roboto-Regular.ttf', 23),
             'company': ImageFont.truetype('Roboto-Regular.ttf',18)
             }
    im = Image.open(resource)
    im_sz = im.size
    im_bg = Image.new(mode='RGBA', size=im_sz, color=(255, 255, 255, 230))
    im_bg.paste(im, (0, 0), 0)
    if image_url:
        im_bg.paste(thumbimg, (101, 160), 0)

    draw = ImageDraw.Draw(im_bg)

    for field in position.keys():
        font = fonts[field]
        if data[field] and (field=='name' or field == 'invited_name'):
            draw.text(map(int, smart_str(position[field]).split(',')), smart_str(data[field]), font=font, fill=(150, 183, 1))
        elif data[field]:
            draw.text(map(int, smart_str(position[field]).split(',')), smart_str(data[field]), font=font, fill=(49, 63, 81))

    im_io = StringIO.StringIO()
    im_bg.save(im_io, format='png')
    im_bg.close()
    im.close()
    im_io.seek(0)

    sharefile = SimpleUploadedFile("%s-%s.png" % \
                                        (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                        im_io.getvalue(), "image/png")

    wizcard.save_email_template(sharefile)

def create_vcard(wizcard):
    v = vobject.vCard()
    v.add('n')
    v.n.value = vobject.vcard.Name(family=wizcard.last_name, given=wizcard.first_name)
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
    if tnurl:
        v.add('photo')
        v.photo.value = tnurl
        v.photo.type_param='jpeg'

    return v.serialize()



@shared_task
def sendmail(from_wizcard,to,template):
    html = 'emailinvite.html'
    emailurl = from_wizcard.emailTemplate.remote_url()

    if template == 'emailscan':
        html = 'emailinfo.html'
        subject = from_wizcard.first_name + " " + from_wizcard.last_name + " has scanned your Business Card"
        emailurl = settings.EMAIL_DEFAULT_IMAGE
    elif template == 'emailscaninvite':
        subject = from_wizcard.first_name + " " + from_wizcard.last_name + " has scanned your Card and Invited you to Connect"

    elif template == 'emailinfo':
        subject = from_wizcard.first_name + " " + from_wizcard.last_name + " has invited you to Connect on WizCard"

    else:
        subject = from_wizcard.first_name + " " + from_wizcard.last_name + " has invited you to Use WizCard and Connect"

    if not emailurl:
        create_template(from_wizcard)
        emailurl = from_wizcard.emailTemplate.remote_url()

    email = Email(to=to, subject=subject)

    ctx = Context({'email_wizcard': emailurl, 'sender_name' : subject})
    email.html(html,ctx)
    #email.html(emailt, ctx)  # Optional
    vcard = from_wizcard.get_vcard
    attach_data = None
    if vcard:
        attach_name = "%s-%s.vcf" % (from_wizcard.first_name, from_wizcard.last_name)
        attach_data = {'data':from_wizcard.get_vcard, 'mime': 'text/vcard', 'name': attach_name}

    email.send(attach=attach_data)

@shared_task
def send_wizcard(from_wizcard, to, emaildetails, half_card = False):

    extfields = from_wizcard.get_ext_fields
    html = emaildetails['template']
    subject = emaildetails['subject']

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
    if half_card == True:
        extfields['sender_phone'] = '***********'
        extfields['sender_email'] = '*****@*****.***'

    email = Email(to=to, subject=subject)
    ctx = Context(extfields)
    email.html(html,ctx)
    attach_data = None
    vcard = from_wizcard.get_vcard
    if half_card == False and vcard:
        attach_name = "%s-%s.vcf" % (from_wizcard.first_name, from_wizcard.last_name)
        attach_data = {'data':from_wizcard.get_vcard, 'mime': 'text/vcard', 'name': attach_name}

    email.send(attach=attach_data)


@shared_task
def send_event(event, to, emaildetails):
    email_dict = dict()
    html = emaildetails['template']
    email_dict['event_name'] = event.name
    email_dict['event_url'] = "http://getwizcard.com/entity/event/%d/product" % event.id

    ctx = Context(email_dict)
    email = Email(to=to, subject = "Welcome to %s - Claim your product space" % event.name)
    email.html(html, ctx)
    email.send(from_addr=emaildetails['from_addr'])

def mass_email(to, id):

    email = Email(to=to, subject="Aren\'t paper business cards such a pain??")

    ctx = Context({'id': id})
    email.html('email_marketing2.html', ctx)
    email.send()
