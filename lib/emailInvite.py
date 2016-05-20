#!/usr/bin/env python
from __future__ import absolute_import
import sys
import StringIO, hashlib
from celery import shared_task
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage as storage
from wizcardship.models import WizcardManager, Wizcard
from wizcard import settings
from PIL import Image,ImageFont, ImageDraw
import pdb
now = timezone.now


@shared_task
def create_template(wizcard_id):

    resource = storage.open(settings.EMAIL_TEMPLATE)

    wizcard = Wizcard.objects.get(id=wizcard_id)

    data = {"name" : wizcard.first_name + " " + wizcard.last_name, "company": wizcard.get_latest_company(), "title" : wizcard.get_latest_title(), "email" : wizcard.email, "phone" : wizcard.phone}
    data["invite_name"] = data["name"]

#    position = {'email': '490,462', 'title': '380,388', 'phone': '198,464', 'name':'378,315', 'company' : '381, 371'}
    position = {'email': '490,462', 'title': '380,388', 'phone': '198,464', 'name':'378,315', 'company' : '381, 371', 'invite_name':'300,600'}
    im = Image.open(resource)
    im_sz = im.size
    im_bg = Image.new(mode='RGBA', size=im_sz, color=(255, 255, 255, 230))
    im_bg.paste(im, (0, 0), 0)
    defaultfont = ImageFont.truetype('Roboto-Regular.ttf', 18)

    try:
        namefont = ImageFont.truetype('Roboto-Bold.ttf', 20)
        invitenamefont = ImageFont.truetype('Robot-Bold.ttf', 45)
    except:
        namefont = ImageFont.truetype('Arial_Bold.ttf', 20)
        invitenamefont = ImageFont.truetype('Arial_Bold.ttf', 45)


    draw = ImageDraw.Draw(im_bg)

    for field in position.keys():
        if field == "name":
            font = namefont
        elif field == "invite_name":
            font = invitenamefont
        else:
            font = defaultfont


        if data[field]:
            draw.text(map(int, str(position[field]).split(',')), str(data[field]), font=font, fill=(0, 0, 0))

    im_io = StringIO.StringIO()
    im_bg.save(im_io, im.format)
    im_bg.close()
    im.close()
    im_io.seek(0)

    sharefile = SimpleUploadedFile("%s-%s.jpg" % \
                                        (wizcard.pk, now().strftime("%Y-%m-%d %H:%M")),
                                        im_io.getvalue(), "image/jpeg")

    wizcard.save_email_template(sharefile)
'''

data = {'email': 'anandramani98@gmail.com', 'company':'Yahoo', 'phone':'8971546485', 'title': 'Director Engg', 'name': 'Anand Ramani'}
position = {'email': '100,150', 'title': '100,200', 'phone': '100,250', 'name':'100,100'}
imgstream = create_template(sys.argv[1], data, position)
f = open("bcard.png","w")
f.write(imgstream.getvalue())
f.close
'''
